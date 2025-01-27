from types import TracebackType

from loguru import logger
from sqlmodel import Session

from src.app.repository import UnitOfWork
from src.resource_adapters.persistence.sqlmodel.database import get_engine
from src.resource_adapters.persistence.sqlmodel.issues import SQLModelIssueRepository


class SQLModelUnitOfWork(UnitOfWork):
    def __init__(self, database_url: str = "sqlite:///./issues.db") -> None:
        self.database_url = database_url
        self._engine = get_engine(database_url)
        self.session: Session | None = None
        self.issues: SQLModelIssueRepository | None = None

    @property
    def engine(self):
        return self._engine

    def commit(self) -> None:
        if self.session:
            self.session.commit()

    def rollback(self) -> None:
        if self.session:
            self.session.rollback()

    def __enter__(self) -> "SQLModelUnitOfWork":
        logger.info("enter sqlmodel uow")
        self.session = Session(self._engine)
        self.issues = SQLModelIssueRepository(self.session)
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        if exc_type:
            logger.info("exit rollback sqlmodel uow")
            self.rollback()
        else:
            logger.info("exit commit sqlmodel uow")
            self.commit()

        if self.session:
            self.session.close()
            self.session = None
            self.issues = None
