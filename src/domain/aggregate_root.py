import abc
from datetime import datetime
from typing import Protocol

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


class AggregateRoot(BaseModel, abc.ABC):
    version: int = 0

    # or handle()
    @abc.abstractmethod
    def process(self, command: BaseCommand) -> list[BaseEvent]:
        pass

    @abc.abstractmethod
    def apply(self, event: BaseEvent) -> None:
        pass
