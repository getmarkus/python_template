from typing import Callable, List

from loguru import logger
from sqlmodel import Session, select

from src.app.ports.repositories.issues import IssueRepository
from src.domain.issue import Issue


class SQLModelIssueRepository(IssueRepository):
    def __init__(self, session: Session) -> None:
        self.session = session

    async def get_by_id(self, id: int) -> Issue:
        logger.info(f"getting issue by id: {id}")
        statement = select(Issue).where(Issue.issue_number == id)
        result = self.session.exec(statement).first()
        if not result:
            return Issue(issue_number=0, version=0)
        return result

    async def list(self) -> List[Issue]:
        statement = select(Issue)
        results = self.session.exec(statement).all()
        return results

    async def list_with_predicate(
        self, predicate: Callable[[Issue], bool]
    ) -> List[Issue]:
        # First get all issues and then filter in memory
        # For better performance, specific predicates could be translated to SQL filters
        all_issues = await self.list()
        return [issue for issue in all_issues if predicate(issue)]

    async def add(self, entity: Issue) -> None:
        logger.info(f"adding issue: {entity.issue_number}")
        self.session.add(entity)

    async def update(self, entity: Issue) -> None:
        logger.info(f"updating issue: {entity}")
        # Use the raw issue number to avoid detached instance issues
        issue_number = entity.issue_number
        statement = select(Issue).where(Issue.issue_number == issue_number)
        existing = self.session.exec(statement).first()
        if existing:
            # Update fields from the detached entity
            existing.issue_state = entity.issue_state
            existing.version = entity.version

    async def remove(self, entity: Issue) -> None:
        logger.info(f"removing issue: {entity}")
        # Use the raw issue number to avoid detached instance issues
        issue_number = entity.issue_number
        statement = select(Issue).where(Issue.issue_number == issue_number)
        existing = self.session.exec(statement).first()
        if existing:
            self.session.delete(existing)
