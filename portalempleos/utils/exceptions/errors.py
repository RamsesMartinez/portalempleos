
class FileValidationException(Exception):
    code = 4002
    status_code = 400
    default_detail = "El archivo no cumple con los requisitos de seguridad"
