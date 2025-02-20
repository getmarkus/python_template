import abc
from datetime import datetime
from typing import Protocol

from sqlmodel import SQLModel


class BaseCommand(Protocol):
    command_id: str
    timestamp: datetime

    # might need specification pattern here
    def validate(self) -> bool: ...


class BaseEvent(Protocol):
    event_id: str
    timestamp: datetime


class AggregateRoot(SQLModel, abc.ABC):
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
