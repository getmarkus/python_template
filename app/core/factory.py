from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.interface_adapters import api_router
from app.interface_adapters.exceptions import AppException
from app.interface_adapters.middleware.error_handler import app_exception_handler
from app.resource_adapters.persistence.sqlmodel.database import get_engine
from config import Settings


def create_app(settings: Settings, lifespan_handler=None) -> FastAPI:
    if lifespan_handler is None:

        @asynccontextmanager
        async def default_lifespan(app: FastAPI):

            # Initialize database if using SQLModel
            get_engine()

            app.state.running = True

            yield

            app.state.running = False

        lifespan_handler = default_lifespan

    app = FastAPI(
        lifespan=lifespan_handler,
        title=settings.project_name,
        openapi_url="/v1/openapi.json",
    )

    # Register global exception handler
    app.add_exception_handler(AppException, app_exception_handler)

    # Register routes
    app.include_router(api_router, prefix="/v1")

    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=(
            [str(origin) for origin in settings.backend_cors_origins]
            if settings.backend_cors_origins
            else ["*"]
        ),
        allow_credentials=settings.cors_allow_credentials,
        allow_methods=settings.cors_allow_methods,
        allow_headers=settings.cors_allow_headers,
        expose_headers=settings.cors_expose_headers,
    )

    return app
