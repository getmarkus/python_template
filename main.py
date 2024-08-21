import datetime
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi_health import health  # type: ignore
from loguru import logger

from src.app_core.config import settings
from src.interface_adapters import api_router

# https://brandur.org/logfmt
# https://github.com/Delgan/loguru
# https://betterstack.com/community/guides/logging/loguru/


running = False


def isRunning() -> bool:
    logger.info(f"running: {running}")
    return running


# https://fastapi.tiangolo.com/advanced/events/
@asynccontextmanager
async def lifespan(app: FastAPI):
    global running
    running = True
    yield
    running = False


def isConfigured():
    logger.info(f"configured: {settings.env_smoke_test == "configured"}")
    return settings.env_smoke_test == "configured"


app = FastAPI(
    lifespan=lifespan, title=settings.project_name, openapi_url=f"/v1/openapi.json"
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
async def root():
    logger.info(f"running: {running}")
    return {
        "app_name": settings.project_name,
        "system_time": datetime.datetime.now(),
    }


# https://docs.paperspace.com/gradient/deployments/healthchecks/
# https://github.com/Kludex/fastapi-health
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
