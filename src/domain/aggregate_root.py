import abc
from datetime import datetime
from typing import Generic, Protocol, TypeVar

from pydantic import BaseModel


class BaseCommand(Protocol):
    command_id: str
    timestamp: datetime

    # might need specification pattern here
    def validate(self) -> bool:
        ...


class BaseEvent(Protocol):
    event_id: str
    timestamp: datetime


TCommand = TypeVar("TCommand", bound=BaseCommand)
TEvent = TypeVar("TEvent", bound=BaseEvent)


class AggregateRoot(BaseModel, Generic[TCommand, TEvent], abc.ABC):
    version: int = 0

    # or handle()
    @abc.abstractmethod
    def process(self, command: TCommand) -> list[TEvent]:
        pass

    @abc.abstractmethod
    def apply(self, event: TEvent) -> None:
        pass
