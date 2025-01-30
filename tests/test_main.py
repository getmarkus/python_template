import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from main import app
from src.resource_adapters.persistence.sqlmodel.database import get_db


# https://sqlmodel.tiangolo.com/tutorial/fastapi/tests/
@pytest.fixture(name="session")
def session_fixture():
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


@pytest.fixture(name="client")
def client_fixture(session: Session):
    def get_session_override():
        return session

    app.dependency_overrides[get_db] = get_session_override
    app.state.running = True
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()
    app.state.running = False


class TestHealth:

    def test_root(self, client: TestClient):
        response = client.get("/")
        assert response.status_code == 200
        assert response.json()["app_name"] == "python-template"

    def test_health(self, client: TestClient):
        response = client.get("/health")
        assert response.status_code == 200

    def test_startup(self, client: TestClient):
        response = client.get("/startup")
        assert response.status_code == 200

    def test_readiness(self, client: TestClient):
        response = client.get("/readiness")
        assert response.status_code == 200

    def test_liveness(self, client: TestClient):
        response = client.get("/liveness")
        assert response.status_code == 200

    def test_smoke(self, client: TestClient):
        response = client.get("/smoke")
        assert response.status_code == 200
