import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session

from app.features.issues.analyze_issue import AnalyzeIssue
from app.domain.issue import Issue, IssueState
from app.core.exceptions import NotFoundException
from app.features.issues.repository import SQLModelIssueRepository


def test_analyze_issue_command(client: TestClient, session: Session):
    # Test case 1: Successful analysis
    issue_number = 1
    test_issue = Issue(issue_number=issue_number, issue_state=IssueState.OPEN)

    uow = SQLModelIssueRepository(session)

    with uow:
        uow.add(test_issue)

    with uow:
        retrieved_issue = uow.get_by_id(issue_number)
        assert retrieved_issue.issue_number == issue_number
        assert retrieved_issue.issue_state == IssueState.OPEN

    use_case = AnalyzeIssue(issue_number=issue_number, repo=uow)
    response = use_case.analyze()
    assert response.issue_number == issue_number


def test_analyze_issue_client(client: TestClient, session: Session):
    # Test case 1: Successful analysis
    issue_number = 1
    test_issue = Issue(issue_number=issue_number, issue_state=IssueState.OPEN)

    uow = SQLModelIssueRepository(session)

    with uow:
        uow.add(test_issue)

    response = client.post("/v1/issues/1/analyze")
    assert response.status_code == 200
    assert response.json() == {"issue_state": "OPEN", "version": 0, "issue_number": 1}


def test_analyze_issue_not_found(client: TestClient, session: Session):
    # Test case 1: Successful analysis
    issue_number = 1

    uow = SQLModelIssueRepository(session)

    with uow:
        retrieved_issue = uow.get_by_id(issue_number)
        assert retrieved_issue.issue_number == 0

    use_case = AnalyzeIssue(issue_number=issue_number, repo=uow)

    with pytest.raises(NotFoundException) as exc_info:
        use_case.analyze()
    assert exc_info.value.message == "Issue not found"

    response = client.post("/v1/issues/1/analyze")
    assert response.status_code == 404


def test_analyze_issue_invalid_number(client: TestClient):
    """Test analyzing an issue with an invalid issue number."""

    response = client.post("/v1/issues/abc/analyze")
    assert response.status_code == 422
    # Validate error response structure
    error_detail = response.json()["detail"]
    assert isinstance(error_detail, list)
    assert error_detail[0]["type"] == "int_parsing"
    assert error_detail[0]["loc"] == ["path", "issue_number"]


# change to test for access permission
def test_analyze_issue_success(client: TestClient, session: Session):
    # Test case 3: Successful analysis with specific issue number

    issue_number = 456
    test_issue = Issue(issue_number=issue_number, issue_state=IssueState.OPEN)

    uow = SQLModelIssueRepository(session)

    with uow:
        uow.add(test_issue)

    response = client.post("/v1/issues/456/analyze")
    assert response.status_code == 200
    assert response.json() == {"issue_state": "OPEN", "version": 0, "issue_number": 456}
    # assert response.status_code == 401
    # assert response.json() == {"detail": "Unauthorized"}
