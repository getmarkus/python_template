from types import TracebackType

from loguru import logger

from src.app_core.repository import ConnectionProtocol, UnitOfWorkProtocol


class Connection(ConnectionProtocol):
    def __init__(self) -> None:
        self.committed = False

    def commit(self) -> None:
        self.committed = True

    def rollback(self) -> None:
        self.committed = False


class UnitOfWork(UnitOfWorkProtocol[ConnectionProtocol]):
    def __init__(self, connection: ConnectionProtocol) -> None:
        self.connection = connection

    def commit(self) -> None:
        self.connection.commit()

    def rollback(self) -> None:
        self.connection.rollback()

    def __enter__(self) -> "UnitOfWorkProtocol[ConnectionProtocol]":
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
