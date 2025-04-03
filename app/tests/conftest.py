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
from config import get_settings

# Specify the custom .env file
dotenv_path = Path(".env.testing")
load_dotenv(dotenv_path=dotenv_path, override=True)


settings = get_settings()


def pytest_unconfigure(config: Config) -> None:
    """Clean up after each test."""
    # Extract database path from the database URL
    db_url = settings.database_url
    if db_url.startswith("sqlite:///") and not db_url.endswith(":memory:"):
        # Remove the sqlite:/// prefix to get the file path
        db_path = db_url.replace("sqlite:///", "")
        # Remove ./ prefix if present
        if db_path.startswith("./"):
            db_path = db_path[2:]

        # Remove test database if it exists
        if os.path.exists(db_path):
            logger.info(f"Removing test database: {db_path}")
            os.remove(db_path)


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
