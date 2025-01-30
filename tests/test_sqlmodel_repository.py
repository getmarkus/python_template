import pytest
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from src.domain.issue import Issue, IssueState
from src.resource_adapters.persistence.sqlmodel.issues import SQLModelIssueRepository


# https://sqlmodel.tiangolo.com/tutorial/fastapi/tests/
class TestSQLModelIssueRepository:
    """Test suite for SQLModel-based issue repository."""

    @pytest.fixture(name="session")
    def session_fixture(self):
        engine = create_engine(
            "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
        )
        SQLModel.metadata.create_all(engine)
        with Session(engine) as session:
            yield session

    def test_add_and_get_issue(self, session: Session):
        """Test adding and retrieving an issue."""
        issue_number = 1
        test_issue = Issue(issue_number=issue_number, issue_state=IssueState.OPEN)

        uow = SQLModelIssueRepository(session)

        with uow:
            uow.add(test_issue)
            uow.commit()

        with uow:
            retrieved_issue = uow.get_by_id(issue_number)
            assert retrieved_issue.issue_number == issue_number
            assert retrieved_issue.issue_state == IssueState.OPEN

    def test_list_issues(self, session: Session):
        """Test listing all issues."""
        issue_number = 1
        test_issue = Issue(issue_number=issue_number, issue_state=IssueState.OPEN)

        uow = SQLModelIssueRepository(session)

        with uow:
            uow.add(test_issue)
            uow.commit()

        with uow:
            issues = uow.list()
            assert len(issues) == 1
            assert issues[0].issue_number == issue_number

    def test_update_issue(self, session: Session):
        """Test updating an issue's state."""
        issue_number = 1
        test_issue = Issue(issue_number=issue_number, issue_state=IssueState.OPEN)

        uow = SQLModelIssueRepository(session)
        with uow:
            uow.add(test_issue)
            uow.commit()

        with uow:
            issue_to_update = uow.get_by_id(issue_number)
            issue_to_update.issue_state = IssueState.CLOSED
            uow.update(issue_to_update)
            uow.commit()

        with uow:
            updated_issue = uow.get_by_id(issue_number)
            assert updated_issue.issue_state == IssueState.CLOSED

    def test_filter_issues(self, session: Session):
        """Test filtering issues with a predicate."""
        issue_number = 1
        test_issue = Issue(issue_number=issue_number, issue_state=IssueState.CLOSED)

        uow = SQLModelIssueRepository(session)
        with uow:
            uow.add(test_issue)
            uow.commit()

        with uow:
            closed_issues = uow.list_with_predicate(
                lambda i: i.issue_state == IssueState.CLOSED
            )
            assert len(closed_issues) == 1

    def test_remove_issue(self, session: Session):
        """Test removing an issue."""
        issue_number = 1
        test_issue = Issue(issue_number=issue_number, issue_state=IssueState.OPEN)

        uow = SQLModelIssueRepository(session)
        with uow:
            uow.add(test_issue)
            uow.commit()

        with uow:
            issue_to_remove = uow.get_by_id(issue_number)
            uow.remove(issue_to_remove)
            uow.commit()

        with uow:
            remaining_issues = uow.list()
            assert len(remaining_issues) == 0
