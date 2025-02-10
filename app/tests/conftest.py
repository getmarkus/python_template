import os
from contextlib import asynccontextmanager

import pytest
from _pytest.config import Config
from _pytest.nodes import Item
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlmodel import Session, delete

from app.core.factory import create_app
from app.resource_adapters.persistence.sqlmodel.database import get_engine
from app.resource_adapters.persistence.sqlmodel.issues import Issue


def pytest_configure(config: Config) -> None:
    """Register env marker."""
    config.addinivalue_line(
        "markers", "env(name): mark test to run only on named environment"
    )


def pytest_runtest_setup(item: Item) -> None:
    """Set up environment for each test based on env marker."""
    envnames = [mark.args[0] for mark in item.iter_markers(name="env")]
    if envnames:
        # Set environment to the first env marker found
        os.environ["APP_ENV"] = envnames[0]
    else:
        # Default to testing environment if no env marker
        os.environ["APP_ENV"] = "testing"


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
app = create_app(lifespan_handler=test_lifespan)


@pytest.fixture(name="session")
def test_session():
    """Session fixture for testing environment using test database."""
    with Session(get_engine()) as session:
        yield session
        statement = delete(Issue)
        session.exec(statement)
        session.commit()


@pytest.fixture(name="client")
def client_fixture():
    with TestClient(app) as client:
        yield client
