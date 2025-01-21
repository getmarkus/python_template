from fastapi import Request
from fastapi.responses import JSONResponse
from loguru import logger

from src.interface_adapters.exceptions import AppException


async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
    """Global exception handler for AppException and its subclasses"""
    logger.error(f"Request to {request.url} failed: {exc.message}")
    if exc.detail:
        logger.error(f"Detail: {exc.detail}")
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "message": exc.message,
            "detail": exc.detail,
            "path": str(request.url)
        }
    )
