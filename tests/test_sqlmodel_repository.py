from sqlmodel import Session, and_

from app.domain.issue import Issue, IssueState
from app.features.issues.repository import SQLModelIssueRepository


def test_add_and_get_issue(session: Session):
    """Test adding and retrieving an issue."""
    issue_number = 1
    test_issue = Issue(issue_number=issue_number, issue_state=IssueState.OPEN)

    uow = SQLModelIssueRepository(session)

    with uow:
        uow.add(test_issue)

    with uow:
        retrieved_issue = uow.get_by_id(issue_number)
        assert retrieved_issue.issue_number == issue_number
        assert retrieved_issue.issue_state == IssueState.OPEN


def test_list_issues(session: Session):
    """Test listing all issues."""
    issue_number = 1
    test_issue = Issue(issue_number=issue_number, issue_state=IssueState.OPEN)

    uow = SQLModelIssueRepository(session)

    with uow:
        uow.add(test_issue)

    with uow:
        issues = uow.list()
        assert len(issues) == 1
        assert issues[0].issue_number == issue_number


def test_update_issue(session: Session):
    """Test updating an issue's state."""
    issue_number = 1
    test_issue = Issue(issue_number=issue_number, issue_state=IssueState.OPEN)

    uow = SQLModelIssueRepository(session)
    with uow:
        uow.add(test_issue)

    with uow:
        issue_to_update = uow.get_by_id(issue_number)
        issue_to_update.issue_state = IssueState.CLOSED
        uow.update(issue_to_update)

    with uow:
        updated_issue = uow.get_by_id(issue_number)
        assert updated_issue.issue_state == IssueState.CLOSED


def test_filter_issues(session: Session):
    """Test filtering issues with a predicate."""
    issue_number = 1
    test_issue = Issue(issue_number=issue_number, issue_state=IssueState.CLOSED)

    uow = SQLModelIssueRepository(session)
    with uow:
        uow.add(test_issue)

    with uow:
        closed_issues = uow.list_with_predicate(
            lambda i: i.issue_state == IssueState.CLOSED
        )
        assert len(closed_issues) == 1


def test_filter_issues_with_sql_predicate(session: Session):
    """Test filtering issues with a SQL Column predicate."""
    # Create two issues with different states
    closed_issue = Issue(issue_number=1, issue_state=IssueState.CLOSED)
    open_issue = Issue(issue_number=2, issue_state=IssueState.OPEN)

    uow = SQLModelIssueRepository(session)
    with uow:
        uow.add(closed_issue)
        uow.add(open_issue)

    with uow:
        # Test filtering using SQL Column predicate
        closed_issues = uow.list_with_predicate(Issue.issue_state == IssueState.CLOSED)
        assert len(closed_issues) == 1
        assert closed_issues[0].issue_number == 1
        assert closed_issues[0].issue_state == IssueState.CLOSED

        # Test filtering using another SQL Column predicate
        open_issues = uow.list_with_predicate(Issue.issue_state == IssueState.OPEN)
        assert len(open_issues) == 1
        assert open_issues[0].issue_number == 2
        assert open_issues[0].issue_state == IssueState.OPEN

        # Test filtering with complex AND condition
        complex_filter = and_(
            Issue.issue_state == IssueState.OPEN, Issue.issue_number > 1
        )
        print(f"Type of complex_filter: {type(complex_filter)}")
        filtered_issues = uow.list_with_predicate(complex_filter)
        assert len(filtered_issues) == 1
        assert filtered_issues[0].issue_number == 2
        assert filtered_issues[0].issue_state == IssueState.OPEN


def test_remove_issue(session: Session):
    """Test removing an issue."""
    issue_number = 1
    test_issue = Issue(issue_number=issue_number, issue_state=IssueState.OPEN)

    uow = SQLModelIssueRepository(session)
    with uow:
        uow.add(test_issue)

    with uow:
        issue_to_remove = uow.get_by_id(issue_number)
        uow.remove(issue_to_remove)

    with uow:
        remaining_issues = uow.list()
        assert len(remaining_issues) == 0
