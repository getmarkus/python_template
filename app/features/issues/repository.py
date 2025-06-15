from typing import Callable, Iterable, List, Protocol, Union

from loguru import logger
from sqlalchemy.sql.elements import BinaryExpression, BooleanClauseList, ClauseElement
from sqlmodel import Session, select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.domain.issue import Issue
from app.core.resource_adapters.persistence.sqlmodel.unit_of_work import SQLModelUnitOfWork, AsyncSQLModelUnitOfWork


class IssueRepository(Protocol):
    # or get
    def get_by_id(self, id: int) -> Issue:
        ...

    # or get_all
    def list(self) -> Iterable[Issue]:
        # return []
        ...

    def list_with_predicate(self, predicate: Callable[[Issue], bool]) -> Iterable[Issue]:
        # for item in self.list():
        #    if predicate(item):
        #        yield item
        # return filter(predicate, self.list())
        ...

    def add(self, entity: Issue) -> None:
        ...

    def update(self, entity: Issue) -> None:
        ...

    def remove(self, entity: Issue) -> None:
        ...


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

    def list_with_predicate(
        self, predicate: Union[Callable[[Issue], bool], ClauseElement]
    ) -> List[Issue]:
        if isinstance(predicate, (BinaryExpression, BooleanClauseList)):
            # If we're passed a SQLModel/SQLAlchemy filter condition, use it directly
            # open_issues = repo.list_with_predicate(Issue.issue_state == IssueState.OPEN)
            statement = select(Issue).where(predicate)
            return self.session.exec(statement).all()
        else:
            # Fall back to in-memory filtering for complex predicates that can't be expressed in SQL
            # open_issues = repository.list_with_predicate(lambda issue: issue.issue_state == IssueState.OPEN)
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
            self.session.add(existing)

    def remove(self, entity: Issue) -> None:
        logger.info(f"removing issue: {entity}")
        # Use the raw issue number to avoid detached instance issues
        issue_number = entity.issue_number
        statement = select(Issue).where(Issue.issue_number == issue_number)
        existing = self.session.exec(statement).first()
        if existing:
            self.session.delete(existing)


class AsyncSQLModelIssueRepository(AsyncSQLModelUnitOfWork, IssueRepository):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    async def get_by_id(self, id: int) -> Issue:
        logger.info(f"getting issue by id: {id}")
        statement = select(Issue).where(Issue.issue_number == id)
        result = await self.session.exec(statement)
        issue = result.first()
        if not issue:
            return Issue(issue_number=0, version=0)
        return issue

    async def list(self) -> List[Issue]:
        statement = select(Issue)
        result = await self.session.exec(statement)
        return result.all()

    async def list_with_predicate(
        self, predicate: Union[Callable[[Issue], bool], ClauseElement]
    ) -> List[Issue]:
        if isinstance(predicate, (BinaryExpression, BooleanClauseList)):
            statement = select(Issue).where(predicate)
            result = await self.session.exec(statement)
            return result.all()
        all_issues = await self.list()
        return [issue for issue in all_issues if predicate(issue)]

    async def add(self, entity: Issue) -> None:
        logger.info(f"adding issue: {entity.issue_number}")
        self.session.add(entity)

    async def update(self, entity: Issue) -> None:
        logger.info(f"updating issue: {entity}")
        issue_number = entity.issue_number
        statement = select(Issue).where(Issue.issue_number == issue_number)
        result = await self.session.exec(statement)
        existing = result.first()
        if existing:
            existing.issue_state = entity.issue_state
            existing.version = entity.version
            self.session.add(existing)

    async def remove(self, entity: Issue) -> None:
        logger.info(f"removing issue: {entity}")
        issue_number = entity.issue_number
        statement = select(Issue).where(Issue.issue_number == issue_number)
        result = await self.session.exec(statement)
        existing = result.first()
        if existing:
            self.session.delete(existing)
