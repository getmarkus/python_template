import pytest
from fastapi.testclient import TestClient

from src.interface_adapters.routers.issues import router

client = TestClient(router)


def test_analyze_issue():
    # Test case 1: Successful analysis
    response = client.post("/issues/123/analyze")
    assert response.status_code == 200
    assert response.json() == {"issue_number": 123, "status": "analyzed"}

    # Test case 2: Invalid issue number
    response = client.post("/issues/abc/analyze")
    assert response.status_code == 422
    assert response.json() == {"detail": "Invalid issue number"}

    # Test case 3: Unauthorized access
    response = client.post("/issues/456/analyze")
    assert response.status_code == 401
    assert response.json() == {"detail": "Unauthorized"}

    # Add more test cases as needed
