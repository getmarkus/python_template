import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, delete

from app.resource_adapters.persistence.sqlmodel.database import get_engine, get_db
from app.resource_adapters.persistence.sqlmodel.issues import Issue
from main import app


@pytest.fixture(name="session", autouse=True)
def session_fixture():

    with Session(get_engine()) as session:
        yield session
        statement = delete(Issue)
        session.exec(statement)
        session.commit()


@pytest.fixture(name="client")
def client_fixture(session: Session):
    def get_session_override():  
        return session

    app.dependency_overrides[get_db] = get_session_override

    with TestClient(app) as client:
        yield client
        app.dependency_overrides.clear()
