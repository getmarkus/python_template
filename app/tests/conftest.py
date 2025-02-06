from contextlib import asynccontextmanager

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlmodel import Session, delete

from app.core.factory import create_app
from app.resource_adapters.persistence.sqlmodel.database import get_engine
from app.resource_adapters.persistence.sqlmodel.issues import Issue


@asynccontextmanager
async def test_lifespan(app: FastAPI):
    yield


# Create test app using the factory with test lifespan
app = create_app(lifespan_handler=test_lifespan)


@pytest.fixture(name="session", autouse=True)
def session_fixture():
    with Session(get_engine()) as session:
        yield session
        statement = delete(Issue)
        session.exec(statement)
        session.commit()


@pytest.fixture(name="client")
def client_fixture():
    with TestClient(app) as client:
        yield client
