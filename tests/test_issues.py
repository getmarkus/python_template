from fastapi.testclient import TestClient
import pytest
from sqlmodel import SQLModel, Session, create_engine
from sqlmodel.pool import StaticPool

from main import app
from src.domain.issue import Issue, IssueState
from src.resource_adapters.persistence.sqlmodel.database import get_db
from src.resource_adapters.persistence.sqlmodel.issues import SQLModelIssueRepository
from src.app.usecases.analyze_issue import AnalyzeIssue
from src.interface_adapters.exceptions import NotFoundException


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


class TestAnalyzeIssue:
    def test_analyze_issue_command(self, client: TestClient, session: Session):
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

    def test_analyze_issue_client(self, client: TestClient, session: Session):
        # Test case 1: Successful analysis
        response = client.post("/issues/1/analyze")
        #assert response.status_code == 200
        assert response.json() == {"version": 1, "issue_number": 1}
    
    def test_analyze_issue_not_found(self, client: TestClient, session: Session):
        # Test case 1: Successful analysis
        issue_number = 1

        repository = SQLModelIssueRepository(session)
        retrieved_issue = repository.get_by_id(issue_number)
        assert retrieved_issue.issue_number == 0

        use_case = AnalyzeIssue(issue_number=issue_number, repo=repository)
        with pytest.raises(NotFoundException) as exc_info:
            use_case.analyze()
        assert exc_info.value.message == "Issue not found"

        response = client.post("/issues/1/analyze")
        assert response.status_code == 404

    def test_analyze_issue_invalid_number(self, client: TestClient, session: Session):
        """Test analyzing an issue with an invalid issue number."""

        response = client.post("/issues/abc/analyze")
        assert response.status_code == 422
        # Validate error response structure
        error_detail = response.json()["detail"]
        assert isinstance(error_detail, list)
        assert error_detail[0]["type"] == "int_parsing"
        assert error_detail[0]["loc"] == ["path", "issue_number"]

    def test_analyze_issue_unauthorized(self, client: TestClient):
        # Test case 3: Unauthorized access
        response = client.post("/issues/456/analyze")
        assert response.status_code == 401
        assert response.js_on() == {"detail": "Unauthorized"}

        # Add more test cases as needed
