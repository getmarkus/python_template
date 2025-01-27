import pytest
from sqlmodel import SQLModel

from src.domain.issue import Issue, IssueState
from src.resource_adapters.persistence.sqlmodel.database import get_engine
from src.resource_adapters.persistence.sqlmodel.unit_of_work import SQLModelUnitOfWork


@pytest.fixture
def uow():
    """Create a SQLModelUnitOfWork with in-memory database."""
    # Reset the global engine for each test
    import src.resource_adapters.persistence.sqlmodel.database as db

    db._engine = None

    # Create a fresh database
    database_url = "sqlite://"
    uow = SQLModelUnitOfWork(database_url=database_url)
    engine = get_engine(database_url)
    SQLModel.metadata.create_all(engine)
    return uow


class TestSQLModelRepository:
    """Test suite for SQLModel-based issue repository."""

    @pytest.mark.anyio
    async def test_add_and_get_issue(self, uow):
        """Test adding and retrieving an issue."""
        issue_number = 1
        test_issue = Issue(issue_number=issue_number, issue_state=IssueState.OPEN)

        with uow:
            await uow.issues.add(test_issue)
            uow.commit()

        with uow:
            retrieved_issue = await uow.issues.get_by_id(issue_number)
            assert retrieved_issue.issue_number == issue_number
            assert retrieved_issue.issue_state == IssueState.OPEN

    @pytest.mark.anyio
    async def test_list_issues(self, uow):
        """Test listing all issues."""
        issue_number = 1
        test_issue = Issue(issue_number=issue_number, issue_state=IssueState.OPEN)

        with uow:
            await uow.issues.add(test_issue)
            uow.commit()

        with uow:
            issues = await uow.issues.list()
            assert len(issues) == 1
            assert issues[0].issue_number == issue_number

    @pytest.mark.anyio
    async def test_update_issue(self, uow):
        """Test updating an issue's state."""
        issue_number = 1
        test_issue = Issue(issue_number=issue_number, issue_state=IssueState.OPEN)

        with uow:
            await uow.issues.add(test_issue)
            uow.commit()

        with uow:
            issue_to_update = await uow.issues.get_by_id(issue_number)
            issue_to_update.issue_state = IssueState.CLOSED
            await uow.issues.update(issue_to_update)
            uow.commit()

        with uow:
            updated_issue = await uow.issues.get_by_id(issue_number)
            assert updated_issue.issue_state == IssueState.CLOSED

    @pytest.mark.anyio
    async def test_filter_issues(self, uow):
        """Test filtering issues with a predicate."""
        issue_number = 1
        test_issue = Issue(issue_number=issue_number, issue_state=IssueState.CLOSED)

        with uow:
            await uow.issues.add(test_issue)
            uow.commit()

        with uow:
            closed_issues = await uow.issues.list_with_predicate(
                lambda i: i.issue_state == IssueState.CLOSED
            )
            assert len(closed_issues) == 1

    @pytest.mark.anyio
    async def test_remove_issue(self, uow):
        """Test removing an issue."""
        issue_number = 1
        test_issue = Issue(issue_number=issue_number, issue_state=IssueState.OPEN)

        with uow:
            await uow.issues.add(test_issue)
            uow.commit()

        with uow:
            issue_to_remove = await uow.issues.get_by_id(issue_number)
            await uow.issues.remove(issue_to_remove)
            uow.commit()

        with uow:
            remaining_issues = await uow.issues.list()
            assert len(remaining_issues) == 0
