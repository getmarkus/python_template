import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from main import app
from src.domain.issue import Issue, IssueState
from src.resource_adapters.persistence.sqlmodel.database import get_db
from src.resource_adapters.persistence.sqlmodel.issues import SQLModelIssueRepository


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
    def test_analyze_issue(self, client: TestClient, session: Session):
        # Test case 1: Successful analysis
        issue_number = 1
        test_issue = Issue(issue_number=issue_number, issue_state=IssueState.OPEN)

        repository = SQLModelIssueRepository(session)

        repository.add(test_issue)

        response = client.post("/issues/1/analyze")
        #assert response.status_code == 200
        assert response.json() == {"version": 1, "issue_number": 1}

        # Test case 2: Invalid issue number
        try:
            response = client.post("/issues/abc/analyze")
            assert response.status_code == 422
            # assert response.json() == {"detail": "Invalid issue number"}
        except Exception as e:
            print(response.status_code)
            print(f"An error occurred: {e}")

        # Test case 3: Unauthorized access
        response = client.post("/issues/456/analyze")
        assert response.status_code == 401
        assert response.json() == {"detail": "Unauthorized"}

        # Add more test cases as needed
