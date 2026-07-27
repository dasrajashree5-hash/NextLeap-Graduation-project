"""Application errors and HTTP mapping."""

from fastapi import Request
from fastapi.responses import JSONResponse


class AppError(Exception):
    def __init__(self, message: str, status_code: int = 400, code: str = "app_error"):
        self.message = message
        self.status_code = status_code
        self.code = code
        super().__init__(message)


class NotFoundError(AppError):
    def __init__(self, message: str = "Resource not found"):
        super().__init__(message, status_code=404, code="not_found")


class ServiceUnavailableError(AppError):
    def __init__(self, message: str = "Dependency unavailable"):
        super().__init__(message, status_code=503, code="service_unavailable")


class ValidationError(AppError):
    def __init__(self, message: str, details=None):
        self.details = details or []
        super().__init__(message, status_code=422, code="validation_error")


async def app_error_handler(_request: Request, exc: AppError) -> JSONResponse:
    body = {"error": {"code": exc.code, "message": exc.message}}
    if isinstance(exc, ValidationError):
        body["details"] = exc.details
    return JSONResponse(
        status_code=exc.status_code,
        content=body,
    )
