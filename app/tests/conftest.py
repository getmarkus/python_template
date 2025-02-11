import os
from contextlib import asynccontextmanager

import pytest
from _pytest.config import Config
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlmodel import Session, delete

from app.core.factory import create_app
from app.resource_adapters.persistence.sqlmodel.database import get_engine
from app.resource_adapters.persistence.sqlmodel.issues import Issue
from config import settings


@pytest.fixture(scope="session", autouse=True)
def set_test_settings():
    """Fixture to force the use of the 'testing' environment for all tests."""
    settings.configure(FORCE_ENV_FOR_DYNACONF="testing")


def pytest_unconfigure(config: Config) -> None:
    """Clean up after each test."""
    # Remove test database if it exists
    if os.path.exists("test.db"):
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
    return create_app(lifespan_handler=test_lifespan)


@pytest.fixture(name="session")
def test_session():
    """Session fixture for testing environment using test database."""
    with Session(get_engine()) as session:
        yield session
        statement = delete(Issue)
        session.exec(statement)
        session.commit()


@pytest.fixture(name="client")
def client_fixture(app: FastAPI):
    with TestClient(app) as client:
        yield client
