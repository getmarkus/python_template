from fastapi.testclient import TestClient

from main import app


def test_root():
    with TestClient(app) as client:
        response = client.get("/")
        assert response.status_code == 200
        assert response.json()["app_name"] == "python-template"


def test_health():
    with TestClient(app) as client:
        response = client.get("/health")
        assert response.status_code == 200


def test_startup():
    with TestClient(app) as client:
        response = client.get("/startup")
        assert response.status_code == 200


def test_readiness():
    with TestClient(app) as client:
        response = client.get("/readiness")
        assert response.status_code == 200


def test_liveness():
    with TestClient(app) as client:
        response = client.get("/liveness")
        assert response.status_code == 200


def test_smoke():
    with TestClient(app) as client:
        response = client.get("/smoke")
        assert response.status_code == 200
