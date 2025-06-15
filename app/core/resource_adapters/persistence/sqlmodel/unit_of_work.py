from types import TracebackType

from loguru import logger
from sqlmodel import Session
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.unit_of_work import UnitOfWork


class SQLModelUnitOfWork(UnitOfWork):
    def __init__(self, session: Session | None = None) -> None:
        self.session: Session = session

    def commit(self) -> None:
        if self.session:
            self.session.commit()

    def rollback(self) -> None:
        if self.session:
            self.session.rollback()

    def __enter__(self) -> "SQLModelUnitOfWork":
        logger.info("enter sqlmodel uow")
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


class AsyncSQLModelUnitOfWork(UnitOfWork):
    def __init__(self, session: AsyncSession | None = None) -> None:
        self.session: AsyncSession = session

    async def commit(self) -> None:
        if self.session:
            await self.session.commit()

    async def rollback(self) -> None:
        if self.session:
            await self.session.rollback()

    async def __aenter__(self) -> "AsyncSQLModelUnitOfWork":
        logger.info("enter async sqlmodel uow")
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        if exc_type:
            logger.info("exit rollback async sqlmodel uow")
            await self.rollback()
        else:
            logger.info("exit commit async sqlmodel uow")
            await self.commit()

        if self.session:
            await self.session.close()
