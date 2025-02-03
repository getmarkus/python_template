import pytest
from fastapi.testclient import TestClient

from main import app



# https://sqlmodel.tiangolo.com/tutorial/fastapi/tests/
# @pytest.fixture(name="session")
# def session_fixture():
#     engine = create_engine(
#         "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
#     )
#     SQLModel.metadata.create_all(engine)
#     with Session(engine) as session:
#         yield session


@pytest.fixture(name="client")
def client_fixture():
    # def get_session_override():
    #     return session

    # app.dependency_overrides[get_db] = get_session_override

    with TestClient(app) as client:
        yield client
        #app.dependency_overrides.clear()


def test_root(client: TestClient):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["app_name"] == "python-template"

def test_health(client: TestClient):
    response = client.get("/health")
    assert response.status_code == 200

def test_startup(client: TestClient):
    response = client.get("/startup")
    assert response.status_code == 200

def test_readiness(client: TestClient):
    response = client.get("/readiness")
    assert response.status_code == 200

def test_liveness(client: TestClient):
    response = client.get("/liveness")
    assert response.status_code == 200

def test_smoke(client: TestClient):
    response = client.get("/smoke")
    assert response.status_code == 200

def test_info(client: TestClient):
    response = client.get("/info")
    assert response.status_code == 200
    data = response.json()
    assert "app_name" in data
    assert data["app_name"] == "python-template"
    assert "system_time" in data
    assert "execution_mode" in data
    assert "env_smoke_test" in data
    assert data["env_smoke_test"] == "configured"

