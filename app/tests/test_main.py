import pytest
from fastapi.testclient import TestClient

from main import app


@pytest.fixture(name="client")
def client_fixture():

    with TestClient(app) as client:
        yield client


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
    assert "database_type" in data


def test_is_configured():
    from main import is_configured

    assert (
        is_configured() is True
    )  # Should be True since project_name is set to "python-template"
