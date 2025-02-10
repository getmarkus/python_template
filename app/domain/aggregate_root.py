import abc
from datetime import datetime
from typing import Protocol

from sqlmodel import SQLModel

from config import settings


class BaseCommand(Protocol):
    command_id: str
    timestamp: datetime

    # might need specification pattern here
    def validate(self) -> bool: ...


class BaseEvent(Protocol):
    event_id: str
    timestamp: datetime


class AggregateRoot(SQLModel, abc.ABC):
    # This sets the database schema in which to create tables for all subclasses of BaseModel
    # __tablename__ = "sometable"
    __table_args__ = {"schema": settings.database_schema}
    version: int = 0

    # or handle()
    @abc.abstractmethod
    def process(self, command: BaseCommand) -> list[BaseEvent]:
        pass

    @abc.abstractmethod
    def apply(self, event: BaseEvent) -> None:
        pass
