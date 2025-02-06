from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.interface_adapters import api_router
from app.interface_adapters.containers import Container
from app.interface_adapters.exceptions import AppException
from app.interface_adapters.middleware.error_handler import app_exception_handler
from app.resource_adapters.persistence.sqlmodel.database import get_engine
from config import settings


def create_container():
    container = Container()
    container.wire(packages=["app"])
    return container


def create_app(lifespan_handler=None) -> FastAPI:
    if lifespan_handler is None:

        @asynccontextmanager
        async def default_lifespan(app: FastAPI):
            # Initialize container and wire dependencies
            container = create_container()

            # Initialize database if using SQLModel
            get_engine()

            app.state.running = True

            yield

            app.state.running = False
            container.unwire()

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

    return app
