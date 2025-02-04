from fastapi import Request
from fastapi.responses import JSONResponse
from loguru import logger

from app.interface_adapters.exceptions import AppException


def app_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    if isinstance(exc, AppException):
        logger.error(f"Request to {request.url} failed: {exc.message}")
        if exc.detail:
            logger.error(f"Detail: {exc.detail}")
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "message": exc.message,
                "detail": exc.detail,
                "path": str(request.url),
            },
        )
    else:
        # Handle other exceptions
        logger.error(f"Request to {request.url} failed: {str(exc)}")
        return JSONResponse(
            status_code=500,
            content={
                "message": "Internal Server Error",
                "detail": str(exc),
                "path": str(request.url),
            },
        )
