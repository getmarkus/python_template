import abc
from datetime import datetime
from typing import Protocol
from config import get_settings

from sqlmodel import SQLModel


class BaseCommand(Protocol):
    command_id: str
    timestamp: datetime

    # might need specification pattern here
    def validate(self) -> bool:
        ...


class BaseEvent(Protocol):
    event_id: str
    timestamp: datetime


class AggregateRoot(SQLModel, abc.ABC, table=False):
    """
    Base class for all aggregate roots in the domain.

    The metadata for this class is injected at runtime using FastAPI's dependency injection.
    Before using this class for database operations, ensure that set_metadata has been called.
    """

    __table_args__ = {"schema": get_settings().get_table_schema}
    version: int = 0

    def __init__(self, **data):
        super().__init__(**data)

    # or handle()
    @abc.abstractmethod
    def process(self, command: BaseCommand) -> list[BaseEvent]:
        pass

    @abc.abstractmethod
    def apply(self, event: BaseEvent) -> None:
        pass
