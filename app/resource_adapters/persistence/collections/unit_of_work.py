from types import TracebackType

from loguru import logger

from app.core.repository import UnitOfWork


class CollectionUnitOfWork(UnitOfWork):
    def __init__(self) -> None:
        self.committed = False

    def commit(self) -> None:
        self.committed = True

    def rollback(self) -> None:
        self.committed = False

    def __enter__(self) -> "CollectionUnitOfWork":
        logger.info("enter uow")
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        if exc_type:
            logger.info("exit rollback uow")
            self.rollback()
        else:
            logger.info("exit commit uow")
            self.commit()
