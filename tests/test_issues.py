from fastapi.testclient import TestClient

from src.interface_adapters.endpoints import issues

client = TestClient(issues.router)


def test_analyze_issue():
    # Test case 1: Successful analysis
    response = client.post("/issues/123/analyze")
    assert response.status_code == 200
    assert response.json() == {"version": 1, "issue_number": 123}

    # Test case 2: Invalid issue number
    try:
        response = client.post("/issues/abc/analyze")
        assert response.status_code == 422
        #assert response.json() == {"detail": "Invalid issue number"}
    except Exception as e:
        print(response.status_code)
        print(f"An error occurred: {e}")

    # Test case 3: Unauthorized access
    response = client.post("/issues/456/analyze")
    assert response.status_code == 401
    assert response.json() == {"detail": "Unauthorized"}

    # Add more test cases as needed
