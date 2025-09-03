# ruff: noqa: E501
import logging

import sentry_sdk
from sentry_sdk.integrations.celery import CeleryIntegration
from sentry_sdk.integrations.django import DjangoIntegration
from sentry_sdk.integrations.logging import LoggingIntegration
from sentry_sdk.integrations.redis import RedisIntegration

from .base import *  # noqa: F403
from .base import DATABASES
from .base import INSTALLED_APPS
from .base import REDIS_URL
from .base import SPECTACULAR_SETTINGS
from .base import env

# GENERAL
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#secret-key
SECRET_KEY = env("DJANGO_SECRET_KEY")
# https://docs.djangoproject.com/en/dev/ref/settings/#allowed-hosts
ALLOWED_HOSTS = env.list("DJANGO_ALLOWED_HOSTS", default=["portalempleos.com.mx"])

# DATABASES
# ------------------------------------------------------------------------------
DATABASES["default"]["CONN_MAX_AGE"] = env.int("CONN_MAX_AGE", default=60)

# CACHES
# ------------------------------------------------------------------------------
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": REDIS_URL,
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            # Mimicking memcache behavior.
            # https://github.com/jazzband/django-redis#memcached-exceptions-behavior
            "IGNORE_EXCEPTIONS": True,
        },
    },
}

# SECURITY
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#secure-proxy-ssl-header
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
# https://docs.djangoproject.com/en/dev/ref/settings/#secure-ssl-redirect
SECURE_SSL_REDIRECT = env.bool("DJANGO_SECURE_SSL_REDIRECT", default=True)
# https://docs.djangoproject.com/en/dev/ref/settings/#session-cookie-secure
SESSION_COOKIE_SECURE = True
# https://docs.djangoproject.com/en/dev/ref/settings/#session-cookie-name
SESSION_COOKIE_NAME = "__Secure-sessionid"
# https://docs.djangoproject.com/en/dev/ref/settings/#csrf-cookie-secure
CSRF_COOKIE_SECURE = True
# https://docs.djangoproject.com/en/dev/ref/settings/#csrf-cookie-name
CSRF_COOKIE_NAME = "__Secure-csrftoken"
# https://docs.djangoproject.com/en/dev/topics/security/#ssl-https
# https://docs.djangoproject.com/en/dev/ref/settings/#secure-hsts-seconds
# TODO: set this to 60 seconds first and then to 518400 once you prove the former works
SECURE_HSTS_SECONDS = 60
# https://docs.djangoproject.com/en/dev/ref/settings/#secure-hsts-include-subdomains
SECURE_HSTS_INCLUDE_SUBDOMAINS = env.bool(
    "DJANGO_SECURE_HSTS_INCLUDE_SUBDOMAINS",
    default=True,
)
# https://docs.djangoproject.com/en/dev/ref/settings/#secure-hsts-preload
SECURE_HSTS_PRELOAD = env.bool("DJANGO_SECURE_HSTS_PRELOAD", default=True)
# https://docs.djangoproject.com/en/dev/ref/middleware/#x-content-type-options-nosniff
SECURE_CONTENT_TYPE_NOSNIFF = env.bool(
    "DJANGO_SECURE_CONTENT_TYPE_NOSNIFF",
    default=True,
)

# Disable ACLs since bucket doesn't support them
AWS_DEFAULT_ACL = env("DJANGO_AWS_DEFAULT_ACL", default=None)
AWS_S3_SECURE_URLS = env.bool("DJANGO_AWS_S3_SECURE_URLS", default=True)
AWS_IS_GZIPPED = env.bool("DJANGO_AWS_IS_GZIPPED", default=True)
AWS_S3_FILE_OVERWRITE = env.bool("DJANGO_AWS_S3_FILE_OVERWRITE", default=False)
AWS_S3_SIGNATURE_VERSION = env.str("DJANGO_AWS_S3_SIGNATURE_VERSION", default="s3v4")

# https://django-storages.readthedocs.io/en/latest/backends/amazon-S3.html#settings
AWS_ACCESS_KEY_ID = env("DJANGO_AWS_ACCESS_KEY_ID")
# https://django-storages.readthedocs.io/en/latest/backends/amazon-S3.html#settings
AWS_SECRET_ACCESS_KEY = env("DJANGO_AWS_SECRET_ACCESS_KEY")
# https://django-storages.readthedocs.io/en/latest/backends/amazon-S3.html#settings
AWS_STORAGE_BUCKET_NAME = env("DJANGO_AWS_STORAGE_BUCKET_NAME")

# Ensure S3 client uses the correct region
AWS_S3_ADDRESSING_STYLE = 'virtual'
# https://django-storages.readthedocs.io/en/latest/backends/amazon-S3.html#settings
AWS_QUERYSTRING_AUTH = env.bool("DJANGO_AWS_QUERYSTRING_AUTH", default=True)
AWS_S3_QUERYSTRING_AUTH = env.bool("DJANGO_AWS_QUERYSTRING_AUTH", default=True)
# DO NOT change these unless you know what you're doing.
_AWS_EXPIRY = 60 * 60 * 24 * 7  # 7 days
# https://django-storages.readthedocs.io/en/latest/backends/amazon-S3.html#settings
AWS_STORAGE_CLASS = env.str("DJANGO_AWS_STORAGE_CLASS", default="STANDARD_IA")
AWS_S3_OBJECT_PARAMETERS = {
    "CacheControl": f"max-age={_AWS_EXPIRY}, s-maxage={_AWS_EXPIRY}, must-revalidate",
    "StorageClass": AWS_STORAGE_CLASS,
}
# https://django-storages.readthedocs.io/en/latest/backends/amazon-S3.html#settings
AWS_S3_MAX_MEMORY_SIZE = env.int(
    "DJANGO_AWS_S3_MAX_MEMORY_SIZE",
    default=100_000_000,  # 100MB
)
AWS_S3_VERIFY = env.bool("DJANGO_AWS_S3_VERIFY", default=True)
# https://django-storages.readthedocs.io/en/latest/backends/amazon-S3.html#settings
AWS_REGION_NAME = env("DJANGO_AWS_S3_REGION_NAME")
AWS_S3_REGION_NAME = AWS_REGION_NAME
# https://django-storages.readthedocs.io/en/latest/backends/amazon-S3.html#cloudfront
AWS_S3_CUSTOM_DOMAIN = env("DJANGO_AWS_S3_CUSTOM_DOMAIN", default=None)

# Build S3 domain with correct region
if AWS_S3_CUSTOM_DOMAIN:
    aws_s3_domain = AWS_S3_CUSTOM_DOMAIN
    AWS_FINAL_S3_DOMAIN = AWS_S3_CUSTOM_DOMAIN
else:
    # Use region-specific endpoint for mx-central-1
    aws_s3_domain = f"{AWS_STORAGE_BUCKET_NAME}.s3.{AWS_S3_REGION_NAME}.amazonaws.com"
    AWS_FINAL_S3_DOMAIN = f"{AWS_STORAGE_BUCKET_NAME}.s3.{AWS_S3_REGION_NAME}.amazonaws.com"
# STATIC & MEDIA
# ------------------------
STORAGES = {
    "default": {
        "BACKEND": "storages.backends.s3.S3Storage",
        "OPTIONS": {
            "location": "media",
            "file_overwrite": False,
        },
    },
    "staticfiles": {
        "BACKEND": "storages.backends.s3.S3StaticStorage",
        "OPTIONS": {
            "location": "static",
            "querystring_auth": True,
            "file_overwrite": True,
        },
    },
}

# Configurar el storage para archivos estáticos
STATICFILES_STORAGE = "storages.backends.s3.S3StaticStorage"

DEFAULT_FILE_STORAGE = "config.storage.MediaRootS3Boto3Storage"
AWS_MEDIA_LOCATION = "media"
MEDIA_URL = f"https://{AWS_FINAL_S3_DOMAIN}/{AWS_MEDIA_LOCATION}/"

# Collectfasta
# ------------------------------------------------------------------------------
# https://github.com/jasongi/collectfasta#installation
# Disabled in production due to conflicts with S3ManifestStaticStorage
# INSTALLED_APPS = ["collectfasta", *INSTALLED_APPS]

# Static files URL
STATIC_URL = f"https://{AWS_FINAL_S3_DOMAIN}/static/"

# EMAIL
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#default-from-email
DEFAULT_FROM_EMAIL = env(
    "DJANGO_DEFAULT_FROM_EMAIL",
    default="Portal Empleos <noreply@portalempleos.com.mx>",
)
# https://docs.djangoproject.com/en/dev/ref/settings/#server-email
SERVER_EMAIL = env("DJANGO_SERVER_EMAIL", default=DEFAULT_FROM_EMAIL)
# https://docs.djangoproject.com/en/dev/ref/settings/#email-subject-prefix
EMAIL_SUBJECT_PREFIX = env(
    "DJANGO_EMAIL_SUBJECT_PREFIX",
    default="[Portal Empleos] ",
)
ACCOUNT_EMAIL_SUBJECT_PREFIX = EMAIL_SUBJECT_PREFIX

# ADMIN
# ------------------------------------------------------------------------------
# Django Admin URL regex.
ADMIN_URL = env("DJANGO_ADMIN_URL")

# Anymail
# ------------------------------------------------------------------------------
# https://anymail.readthedocs.io/en/stable/installation/#installing-anymail
INSTALLED_APPS += ["anymail"]
# https://docs.djangoproject.com/en/dev/ref/settings/#email-backend
# https://anymail.readthedocs.io/en/stable/installation/#anymail-settings-reference
# https://anymail.readthedocs.io/en/stable/esps
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
ANYMAIL = {}

# LOGGING
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#logging
# See https://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.

LOGGING = {
    "version": 1,
    "disable_existing_loggers": True,
    "formatters": {
        "verbose": {
            "format": "%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s",
        },
    },
    "handlers": {
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
    },
    "root": {"level": "INFO", "handlers": ["console"]},
    "loggers": {
        "django.db.backends": {
            "level": "ERROR",
            "handlers": ["console"],
            "propagate": False,
        },
        # Errors logged by the SDK itself
        "sentry_sdk": {"level": "ERROR", "handlers": ["console"], "propagate": False},
        "django.security.DisallowedHost": {
            "level": "ERROR",
            "handlers": ["console"],
            "propagate": False,
        },
    },
}

# Sentry
# ------------------------------------------------------------------------------
# Sentry is optional and can be disabled by setting DJANGO_USE_SENTRY=False
USE_SENTRY = env.bool("DJANGO_USE_SENTRY", default=True)

if USE_SENTRY:
    SENTRY_DSN = env("DJANGO_SENTRY_DSN")
    SENTRY_LOG_LEVEL = env.int("DJANGO_SENTRY_LOG_LEVEL", logging.INFO)

    sentry_logging = LoggingIntegration(
        level=SENTRY_LOG_LEVEL,  # Capture info and above as breadcrumbs
        event_level=logging.ERROR,  # Send errors as events
    )
    integrations = [
        sentry_logging,
        DjangoIntegration(),
        CeleryIntegration(),
        RedisIntegration(),
    ]
    sentry_sdk.init(
        dsn=SENTRY_DSN,
        integrations=integrations,
        environment=env("DJANGO_SENTRY_ENVIRONMENT", default="production"),
        traces_sample_rate=env.float("DJANGO_SENTRY_TRACES_SAMPLE_RATE", default=0.0),
    )
else:
    # Disable Sentry logging when not in use
    LOGGING["loggers"]["sentry_sdk"] = {
        "level": "CRITICAL",
        "handlers": ["console"],
        "propagate": False,
    }

# django-rest-framework
# -------------------------------------------------------------------------------
# Tools that generate code samples can use SERVERS to point to the correct domain
SPECTACULAR_SETTINGS["SERVERS"] = [
    {"url": "https://portalempleos.com.mx", "description": "Production server"},
]
# Your stuff...
# ------------------------------------------------------------------------------
