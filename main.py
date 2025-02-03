import datetime
import os
import uuid
from contextlib import asynccontextmanager
from typing import Annotated, Any, Dict, Optional

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from loguru import logger
from pydantic import BaseModel, Field

from config import Settings
from src.interface_adapters import api_router
from src.interface_adapters.exceptions import AppException
from src.interface_adapters.middleware.error_handler import app_exception_handler

# https://brandur.org/logfmt
# https://github.com/Delgan/loguru
# https://betterstack.com/community/guides/logging/loguru/

env = os.getenv("PYTHON_TEMPLATE_ENV", ".env")

def isRunning() -> bool:
    #logger.info(f"App state: {dict(app.state.__dict__)}")
    running = getattr(app.state, "running", False)
    logger.info(f"Running state: {running}")
    return running


# https://fastapi.tiangolo.com/advanced/events/
@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.running = True
    logger.info("Lifespan started")
    logger.info(f"App state: {dict(app.state.__dict__)}")
    logger.info(app.state.running)

    yield

    app.state.running = False
    logger.info("Lifespan stopped")


def is_configured() -> bool:
    logger.info(f"configured: {Settings.get_settings().env_smoke_test == "configured"}")
    return Settings.get_settings().env_smoke_test == "configured"


""" {
  "status": "pass|fail|warn",  // Required
  "version": "1.0",           // Optional
  "description": "...",       // Optional
  "checks": {                 // Optional, for detailed component status
    "database": {
      "status": "up",
      "responseTime": "23ms"
    },
    "cache": {
      "status": "up",
      "responseTime": "5ms"
    }
  }
} """


class HealthCheck(BaseModel):
    """RFC Health Check response format."""

    status: str = Field(
        ..., description="Required. Status of the service: pass, fail, or warn"
    )
    version: Optional[str] = Field(None, description="Version of the service")
    description: Optional[str] = Field(
        None, description="Human-friendly description of the service"
    )
    checks: Optional[Dict[str, Dict[str, Any]]] = Field(
        None, description="Additional checks"
    )


def create_health_response(is_healthy: bool, check_name: str) -> JSONResponse:
    """Create a standardized health check response."""
    status = "pass" if is_healthy else "fail"
    response = HealthCheck(
        status=status,
        version=Settings.get_settings().project_name,
        description=f"Service {status}",
        checks={
            check_name: {
                "status": status,
                "time": datetime.datetime.now().isoformat(),
            }
        },
    )

    return JSONResponse(
        status_code=200 if is_healthy else 503,
        content=response.model_dump(),
        media_type="application/health+json",
    )


app = FastAPI(
    lifespan=lifespan,
    title=Settings.get_settings().project_name,
    openapi_url="/v1/openapi.json",
)

# Register global exception handler
app.add_exception_handler(AppException, app_exception_handler)

# middleware options
# https://levelup.gitconnected.com/17-useful-middlewares-for-fastapi-that-you-should-know-about-951c2b0869c7
# https://fastapi.tiangolo.com/tutorial/middleware/
# https://http.dev/headers
# CORS
# Authorization and Authentication
# Localization
# Caching
# Rate Limiting
# Tracing
# Dependency Injection
# A/B testing
# Metrics
# Route security, ip address and user agent - TrustedHostMiddleware
# gzip compression - GZipMiddleware
# ssl enforcement - HTTPSRedirectMiddleware

@app.middleware("http")
async def add_request_id(request, call_next):
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    logger.info(f"Request {request_id} to {request.url.path}")
    return response

@app.middleware("http")
async def add_process_time_header(request, call_next):
    import time
    start_time = time.perf_counter()
    response = await call_next(request)
    process_time = time.perf_counter() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    logger.info(f"Request to {request.url.path} took {process_time:.4f} seconds")
    return response

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Set this to lock down if applicable to your use case
    # allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
    allow_credentials=False,  # Must be false if all origins (*) is allowed
    allow_methods=["*"],
    allow_headers=["X-Forwarded-For", "Authorization", "Content-Type", "X-Request-ID"],
    expose_headers=["X-Process-Time", "X-Request-ID"]
)


@app.get("/")
async def root(
    settings: Annotated[Settings, Depends(Settings.get_settings)],
) -> Dict[str, Any]:
    return {
        "app_name": settings.project_name,
        "system_time": datetime.datetime.now(),
    }


@app.get("/info")
async def info(
    settings: Annotated[Settings, Depends(Settings.get_settings)],
) -> Dict[str, Any]:
    logger.info(settings.model_dump())
    return {
        "app_name": settings.project_name,
        "system_time": datetime.datetime.now(),
        "execution_mode": settings.execution_mode,
        "env_smoke_test": settings.env_smoke_test,
    }


# Health check endpoints
# Startup: Signals if the application has completed its initial startup
# Smoke: Verifies basic configuration and dependencies
# Readiness: Shows if the application is ready to handle requests
# Liveness: Indicates if the application is running and alive
# https://datatracker.ietf.org/doc/html/draft-inadarei-api-health-check
@app.get("/health", response_class=JSONResponse)
async def health_check() -> JSONResponse:
    """Overall service health check."""
    return create_health_response(isRunning(), "service")


@app.get("/liveness", response_class=JSONResponse)
async def liveness_check() -> JSONResponse:
    """Service liveness check."""
    return create_health_response(isRunning(), "liveness")


@app.get("/startup", response_class=JSONResponse)
async def startup_check() -> JSONResponse:
    """Startup health check."""
    return create_health_response(isRunning(), "startup")


@app.get("/readiness", response_class=JSONResponse)
async def readiness_check() -> JSONResponse:
    """Service readiness check."""
    return create_health_response(isRunning(), "readiness")


@app.get("/smoke", response_class=JSONResponse)
async def smoke_check() -> JSONResponse:
    """Configuration smoke test."""
    return create_health_response(is_configured(), "configuration")


# add feature routers here
app.include_router(api_router, prefix="/v1")

# if unit test for health check is desired
# https://fastapi.tiangolo.com/advanced/testing-events/
# https://github.com/Kludex/fastapi-health/blob/main/tests/test_endpoint.py

# if metadata output is desired on health check
# https://fastapi.tiangolo.com/tutorial/metadata/

# reverse proxy and system serice manager
# https://medium.com/@kevinzeladacl/deploy-a-fastapi-app-with-nginx-and-gunicorn-b66ac14cdf5a
# https://fastapi.tiangolo.com/advanced/behind-a-proxy/
