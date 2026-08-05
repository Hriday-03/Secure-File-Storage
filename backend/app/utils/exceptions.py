"""Custom application exceptions mapped to structured API errors."""


class AppException(Exception):
    """Base class for all application exceptions."""

    status_code: int = 500
    code: str = "INTERNAL_ERROR"
    message: str = "Something went wrong. Please try again."

    def __init__(self, message: str | None = None) -> None:
        super().__init__(message or self.message)
        self.message = message or self.message


class AuthenticationRequiredError(AppException):
    status_code = 401
    code = "AUTHENTICATION_REQUIRED"
    message = "Authentication is required."


class InvalidCredentialsError(AppException):
    status_code = 401
    code = "INVALID_CREDENTIALS"
    message = "Invalid email or password."


class ForbiddenError(AppException):
    status_code = 403
    code = "FORBIDDEN"
    message = "You do not have permission to perform this action."


class NotFoundError(AppException):
    status_code = 404
    code = "NOT_FOUND"
    message = "Resource not found."


class EmailAlreadyRegisteredError(AppException):
    status_code = 409
    code = "EMAIL_ALREADY_REGISTERED"
    message = "An account with this email already exists."


class ValidationError(AppException):
    status_code = 422
    code = "VALIDATION_ERROR"
    message = "Invalid input provided."


class FileTooLargeError(AppException):
    status_code = 413
    code = "FILE_TOO_LARGE"
    message = "File exceeds the maximum allowed size."


class FileTypeNotAllowedError(AppException):
    status_code = 415
    code = "FILE_TYPE_NOT_ALLOWED"
    message = "This file type is not allowed."


class EmptyFileError(AppException):
    status_code = 422
    code = "EMPTY_FILE"
    message = "Uploaded file is empty."


class EncryptionError(AppException):
    status_code = 500
    code = "ENCRYPTION_ERROR"
    message = "Failed to process the file securely."


class StorageError(AppException):
    status_code = 500
    code = "STORAGE_ERROR"
    message = "Failed to store or retrieve the file."


class DecryptionError(AppException):
    status_code = 500
    code = "DECRYPTION_ERROR"
    message = "Failed to decrypt the file."