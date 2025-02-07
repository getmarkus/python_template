import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session

from app.core.usecases.analyze_issue import AnalyzeIssue
from app.domain.issue import Issue, IssueState
from app.interface_adapters.exceptions import NotFoundException
from app.resource_adapters.persistence.sqlmodel.issues import SQLModelIssueRepository


@pytest.mark.env("testing")
def test_analyze_issue_command(client: TestClient, session: Session):
    # Test case 1: Successful analysis
    issue_number = 1
    test_issue = Issue(issue_number=issue_number, issue_state=IssueState.OPEN)

    repository = SQLModelIssueRepository(session)

    repository.add(test_issue)
    repository.commit()
    retrieved_issue = repository.get_by_id(issue_number)
    assert retrieved_issue.issue_number == issue_number

    use_case = AnalyzeIssue(issue_number=issue_number, repo=repository)
    response = use_case.analyze()
    assert response.issue_number == issue_number


@pytest.mark.env("development")
def test_analyze_issue_client(client: TestClient, session: Session):
    # Test case 1: Successful analysis
    issue_number = 1
    test_issue = Issue(issue_number=issue_number, issue_state=IssueState.OPEN)

    repository = SQLModelIssueRepository(session)

    repository.add(test_issue)
    repository.commit()

    response = client.post("/v1/issues/1/analyze")
    assert response.status_code == 200
    assert response.json() == {"issue_state": "OPEN", "version": 0, "issue_number": 1}


def test_analyze_issue_not_found(client: TestClient, session: Session):
    # Test case 1: Successful analysis
    issue_number = 1

    repository = SQLModelIssueRepository(session)
    retrieved_issue = repository.get_by_id(issue_number)
    assert retrieved_issue.issue_number == 0

    use_case = AnalyzeIssue(issue_number=issue_number, repo=repository)
    with pytest.raises(NotFoundException) as exc_info:
        use_case.analyze()
    assert exc_info.value.message == "Issue not found"

    response = client.post("/v1/issues/1/analyze")
    assert response.status_code == 404


def test_analyze_issue_invalid_number(client: TestClient, session: Session):
    """Test analyzing an issue with an invalid issue number."""

    response = client.post("/v1/issues/abc/analyze")
    assert response.status_code == 422
    # Validate error response structure
    error_detail = response.json()["detail"]
    assert isinstance(error_detail, list)
    assert error_detail[0]["type"] == "int_parsing"
    assert error_detail[0]["loc"] == ["path", "issue_number"]


def test_analyze_issue_unauthorized(client: TestClient):
    # Test case 3: Unauthorized access
    response = client.post("/v1/issues/456/analyze")
    assert response.status_code == 401
    assert response.json() == {"detail": "Unauthorized"}
