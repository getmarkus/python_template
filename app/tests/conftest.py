import os
from contextlib import asynccontextmanager
from pathlib import Path

import pytest
from _pytest.config import Config
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.testclient import TestClient
from loguru import logger
from sqlmodel import Session, delete

from app.core.factory import create_app
from app.resource_adapters.persistence.sqlmodel.database import get_engine
from app.resource_adapters.persistence.sqlmodel.issues import Issue
from config import Settings, get_settings

# Specify the custom .env file
dotenv_path = Path(".env.testing")
load_dotenv(dotenv_path=dotenv_path, override=True)


settings = get_settings()


def pytest_unconfigure(config: Config) -> None:
    """Clean up after each test."""
    # Remove test database if it exists
    if os.path.exists("test.db"):
        logger.info("Removing test database")
        os.remove("test.db")


@asynccontextmanager
async def test_lifespan(app: FastAPI):
    """Test-specific lifespan that sets up and tears down test resources."""
    yield
    # Cleanup will happen in pytest_unconfigure


# Create test app using the factory with test lifespan
@pytest.fixture(name="app")
def test_app():
    """Create test app instance only during test execution."""
    return create_app(settings, lifespan_handler=test_lifespan)


@pytest.fixture(name="session")
def test_session():
    """Session fixture for testing environment using test database."""
    with Session(get_engine(settings)) as session:
        yield session
        statement = delete(Issue)
        session.exec(statement)
        session.commit()


@pytest.fixture(name="client")
def client_fixture(app: FastAPI):
    with TestClient(app) as client:
        yield client
