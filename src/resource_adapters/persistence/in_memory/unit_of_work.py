from types import TracebackType

from loguru import logger

from src.app.repository import UnitOfWork


class UnitOfWork(UnitOfWork):
    def __init__(self) -> None:
        self.committed = False

    def commit(self) -> None:
        self.committed = True

    def rollback(self) -> None:
        self.committed = False

    def __enter__(self) -> "UnitOfWork":
        logger.info(f"enter uow")
        return self

    def __exit__(
        self,
        exc_type: type[BaseException],
        exc_val: BaseException,
        exc_tb: TracebackType,
    ) -> None:
        if exc_type:
            logger.info(f"exit rollback uow")
            self.rollback()
        else:
            logger.info(f"exit commit uow")
            self.commit()
