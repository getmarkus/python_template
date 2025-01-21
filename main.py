from contextlib import asynccontextmanager
import datetime
import os
from typing import Annotated, Any, Dict

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi_health import health
from loguru import logger

from config import Settings
from src.interface_adapters import api_router

# https://brandur.org/logfmt
# https://github.com/Delgan/loguru
# https://betterstack.com/community/guides/logging/loguru/

env = os.getenv("PYTHON_TEMPLATE_ENV", ".env")
running = False


async def isRunning() -> bool:
    logger.info(f"running: {running}")
    return running


# https://fastapi.tiangolo.com/advanced/events/
@asynccontextmanager
async def lifespan(app: FastAPI):
    global running
    running = True
    yield
    running = False


async def isConfigured():
    logger.info(f"configured: {Settings.get_settings().env_smoke_test == "configured"}")
    return Settings.get_settings().env_smoke_test == "configured"


app = FastAPI(
    lifespan=lifespan,
    title=Settings.get_settings().project_name,
    openapi_url="/v1/openapi.json",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Set this to lock down if applicable to your use case
    # allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
    allow_credentials=False,  # Must be false if all origins (*) is allowed
    allow_methods=["*"],
    allow_headers=["X-Forwarded-For", "Authorization", "Content-Type"],
)


@app.get("/")
async def root(
    settings: Annotated[Settings, Depends(Settings.get_settings)],
) -> Dict[str, Any]:
    logger.info(f"running: {running}")
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
        "items_per_user": settings.project_name,
    }


# https://docs.paperspace.com/gradient/deployments/healthchecks/
# https://github.com/Kludex/fastapi-health
# https://github.com/healthchecks/healthchecks
app.add_api_route("/health", health([isRunning]))
app.add_api_route("/startup", health([isRunning]))
app.add_api_route("/readiness", health([isRunning]))
app.add_api_route("/liveness", health([isRunning]))
app.add_api_route("/smoke", health([isConfigured]))

# add feature routers here
app.include_router(api_router, prefix="/v1")

# if unit test for health check is desired
# https://fastapi.tiangolo.com/advanced/testing-events/
# https://github.com/Kludex/fastapi-health/blob/main/tests/test_endpoint.py

# if metadata output is desired on health check
# https://fastapi.tiangolo.com/tutorial/metadata/

# reverse proxy and system serice manager
# https://docs.sisk-framework.org/docs/deploying/production/
# https://medium.com/@kevinzeladacl/deploy-a-fastapi-app-with-nginx-and-gunicorn-b66ac14cdf5a
# https://fastapi.tiangolo.com/advanced/behind-a-proxy/
