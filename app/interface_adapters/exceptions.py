from typing import Optional

class AppException(Exception):
    """Base exception class for application exceptions"""
    def __init__(
        self,
        message: str,
        status_code: int = 500,
        detail: Optional[str] = None
    ) -> None:
        self.message = message
        self.status_code = status_code
        self.detail = detail
        super().__init__(self.message)


class UnsupportedOperationException(AppException):
    """Exception raised when an operation is not supported"""
    def __init__(
        self,
        message: str = "Operation not supported",
        detail: Optional[str] = None
    ) -> None:
        super().__init__(
            message=message,
            status_code=501,
            detail=detail
        )


class ConfigurationException(AppException):
    """Exception raised for configuration errors"""
    def __init__(
        self,
        message: str = "Invalid configuration",
        detail: Optional[str] = None
    ) -> None:
        super().__init__(
            message=message,
            status_code=500,
            detail=detail
        )


class NotFoundException(AppException):
    """Exception raised when a requested resource is not found"""
    def __init__(
        self,
        message: str = "Resource not found",
        detail: Optional[str] = None
    ) -> None:
        super().__init__(
            message=message,
            status_code=404,
            detail=detail
        )
