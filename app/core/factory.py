from contextlib import asynccontextmanager

from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware

from app.features.issues import router as issues_router
from app.core.exceptions import AppException
from app.core.middleware import app_exception_handler
from config import Settings
from app.core.database import get_async_engine, get_engine

# Create API router and include feature routers
api_router = APIRouter()
api_router.include_router(issues_router, tags=["issues"])


def create_app(settings: Settings, lifespan_handler=None) -> FastAPI:
    if lifespan_handler is None:

        @asynccontextmanager
        async def default_lifespan(app: FastAPI):
            # Choose database engine based on configuration
            if settings.is_async_database:
                # Use async engine for async database URLs
                get_async_engine(settings)
            else:
                # For sync database URLs, we need to initialize the engine outside the async context
                # This is done here for simplicity, but in production you might want to
                # use a background task or separate initialization step
                import asyncio
                loop = asyncio.get_event_loop()
                await loop.run_in_executor(None, lambda: get_engine(settings))
                
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
