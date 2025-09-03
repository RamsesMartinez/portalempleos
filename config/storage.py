import logging
import mimetypes
import os
import re
from abc import ABC, abstractmethod
from dataclasses import dataclass

import magic
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from storages.backends.s3boto3 import S3Boto3Storage

from portalempleos.utils.exceptions.errors import FileValidationException


logger = logging.getLogger(__name__)

# MIME type constants from python-magic
MIME_TYPE_PDF = "application/pdf"
MIME_TYPE_PDF_ADOBE = "application/x-pdf"


@dataclass
class FileValidationConfig:
    """Configuration for file validation"""

    allowed_mime_types: list[str]
    allowed_extensions: list[str]
    max_file_size: int = settings.MAX_UPLOAD_SIZE
    require_extension: bool = settings.REQUIRE_FILE_EXTENSION


class FileValidator(ABC):
    """Abstract base class for file validators"""

    @abstractmethod
    def validate(self, content, name: str) -> None:
        """Validate file content and name"""
        pass


class FileSizeValidator(FileValidator):
    """Validates file size"""

    def __init__(self, config: FileValidationConfig):
        self.config = config

    def validate(self, content, name: str) -> None:
        if hasattr(content, "size") and content.size > self.config.max_file_size:
            raise ValidationError(
                f"File size exceeds maximum allowed size of "
                f"{self.config.max_file_size / (1024 * 1024):.1f}MB"
            )


class MimeTypeValidator(FileValidator):
    """Validates file MIME type"""

    def __init__(self, config: FileValidationConfig):
        self.config = config

    def validate(self, content, name: str) -> None:
        # Try to get the MIME type of the content first
        content_type = getattr(content, "content_type", None)

        # If not available, try to detect it by the name
        if not content_type:
            content_type = mimetypes.guess_type(name)[0]

        # If still no MIME type, try to detect it by the content
        if not content_type:
            try:
                content_start = content.read(4096)
                content.seek(0)
                content_type = magic.from_buffer(content_start, mime=True)
            except Exception as e:
                logger.error(f"Error detecting MIME type: {str(e)}")
                raise ValidationError("Could not determine file type")

        if not content_type:
            raise ValidationError("Could not determine file type")

        if content_type not in self.config.allowed_mime_types:
            logging.warning(
                f"File mime type not allowed: {content_type}, current allowed mime types: "
                f"{self.config.allowed_mime_types}"
            )
            raise ValidationError(f"File mime type not allowed: {content_type}")


class ExtensionValidator(FileValidator):
    """Validates file extension"""

    def __init__(self, config: FileValidationConfig):
        self.config = config

    def validate(self, content, name: str) -> None:
        # Get the extension (if exists)
        ext = os.path.splitext(name)[1].lower().replace(".", "")

        # If there is no extension
        if not ext:
            if self.config.require_extension:
                raise ValidationError("Files without extension are not allowed")
            # If extension is not required, validate the MIME type
            try:
                content_start = content.read(4096)
                content.seek(0)
                detected_mime = magic.from_buffer(content_start, mime=True)
                if detected_mime not in self.config.allowed_mime_types:
                    raise ValidationError("File type not allowed")
            except Exception as e:
                logger.error(f"Error validating file without extension: {str(e)}")
                raise ValidationError("Could not validate file type")
            return

        if ext not in self.config.allowed_extensions:
            raise ValidationError(f"File extension not allowed: {ext}")


class PDFSecurityValidator(FileValidator):
    """Validates PDF files for security issues"""

    def __init__(self):
        self.critical_patterns = {
            "openaction": r"/OpenAction\s*<<",  # Auto-open actions
            "javascript": r"/JavaScript\s*",  # Embedded JavaScript
            "js": r"/JS\s*\(",  # JavaScript calls
            "launch": r"/Launch\s*<<",  # External file execution
            "action": r"/AA\s*<<",  # Additional automatic actions
            "acroform": r"/AcroForm\s*<<",  # Forms that may contain JavaScript
            "richmedia": r"/RichMedia\s*<<",  # Potentially dangerous multimedia content
            "embedded_files": r"/EmbeddedFiles\s*<<",  # Embedded files
        }

    def validate(self, content, name: str) -> None:
        try:
            content_start = content.read(4096)
            content.seek(0)
            detected_mime = magic.from_buffer(content_start, mime=True)

            # Only validate if it is a PDF (by content)
            if detected_mime not in [MIME_TYPE_PDF, MIME_TYPE_PDF_ADOBE]:
                return

            content_bytes = content.read()
            content.seek(0)
            content_str = content_bytes.decode("latin-1")

            for pattern_name, pattern in self.critical_patterns.items():
                if re.search(pattern, content_str, re.IGNORECASE):
                    logger.warning(
                        f"Malicious PDF pattern detected: {pattern_name}",
                        extra={
                            "pattern_found": pattern_name,
                            "file_size": len(content_bytes),
                            "file_name": name,
                        },
                    )
                    raise FileValidationException(
                        _("PDF contains potentially malicious content")
                    )

        except UnicodeDecodeError:
            logger.warning("Invalid PDF content structure detected")
            raise FileValidationException(_("Invalid PDF content structure"))
        except FileValidationException:
            raise
        except Exception as e:
            logger.exception(f"Error validating PDF: {str(e)}")
            raise FileValidationException(
                _(
                    "An unexpected error occurred while validating the file. Please try with another file."
                )
            )


class SecureFileValidator:
    """Composite validator that runs multiple validation strategies"""

    def __init__(self, config: FileValidationConfig):
        self.validators: list[FileValidator] = [
            FileSizeValidator(config),
            MimeTypeValidator(config),
            ExtensionValidator(config),
            PDFSecurityValidator(),
        ]

    def validate(self, content, name: str) -> None:
        """Run all validators"""
        for validator in self.validators:
            validator.validate(content, name)


class SecureS3Storage(S3Boto3Storage):
    """S3 storage with security validations"""

    def __init__(self):
        super().__init__()
        self.config = FileValidationConfig(
            allowed_mime_types=settings.ALLOWED_UPLOAD_TYPES,
            allowed_extensions=settings.ALLOWED_UPLOAD_EXTENSIONS,
            max_file_size=settings.MAX_UPLOAD_SIZE,
            require_extension=settings.REQUIRE_FILE_EXTENSION,
        )
        self.validator = SecureFileValidator(self.config)

    def _save(self, name: str, content) -> str:
        # Validate file
        self.validator.validate(content, name)

        # Configure S3 parameters
        self.object_parameters = {
            "ContentType": (
                content.content_type
                if hasattr(content, "content_type")
                else mimetypes.guess_type(name)[0]
            ),
            "ContentDisposition": "attachment",
            "CacheControl": "no-cache, no-store, must-revalidate",
            "ServerSideEncryption": "AES256",
        }

        return super()._save(name, content)


class MediaRootS3Boto3Storage(SecureS3Storage):
    """Storage for media files"""

    location = settings.AWS_MEDIA_LOCATION
    default_acl = "private"
    file_overwrite = False


class StaticRootS3Boto3Storage(S3Boto3Storage):
    """Storage for static files"""
    
    location = "static"
    default_acl = "public-read"
    file_overwrite = True
