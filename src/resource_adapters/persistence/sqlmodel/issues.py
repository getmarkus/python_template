from typing import Callable, List

from loguru import logger
from sqlmodel import Session, select

from src.app.ports.repositories.issues import IssueRepository
from src.domain.issue import Issue
from src.resource_adapters.persistence.sqlmodel.unit_of_work import SQLModelUnitOfWork


class SQLModelIssueRepository(SQLModelUnitOfWork, IssueRepository):
    def __init__(self, session: Session) -> None:
        super().__init__(session)

    def get_by_id(self, id: int) -> Issue:
        logger.info(f"getting issue by id: {id}")
        statement = select(Issue).where(Issue.issue_number == id)
        result = self.session.exec(statement).first()
        if not result:
            return Issue(issue_number=0, version=0)
        return result

    def list(self) -> List[Issue]:
        statement = select(Issue)
        results = self.session.exec(statement).all()
        return results

    def list_with_predicate(self, predicate: Callable[[Issue], bool]) -> List[Issue]:
        # First get all issues and then filter in memory
        # For better performance, specific predicates could be translated to SQL filters
        all_issues = self.list()
        return [issue for issue in all_issues if predicate(issue)]

    def add(self, entity: Issue) -> None:
        logger.info(f"adding issue: {entity.issue_number}")
        self.session.add(entity)

    def update(self, entity: Issue) -> None:
        logger.info(f"updating issue: {entity}")
        # Use the raw issue number to avoid detached instance issues
        issue_number = entity.issue_number
        statement = select(Issue).where(Issue.issue_number == issue_number)
        existing = self.session.exec(statement).first()
        if existing:
            # Update fields from the detached entity
            existing.issue_state = entity.issue_state
            existing.version = entity.version

    def remove(self, entity: Issue) -> None:
        logger.info(f"removing issue: {entity}")
        # Use the raw issue number to avoid detached instance issues
        issue_number = entity.issue_number
        statement = select(Issue).where(Issue.issue_number == issue_number)
        existing = self.session.exec(statement).first()
        if existing:
            self.session.delete(existing)
