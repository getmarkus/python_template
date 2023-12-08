from datetime import datetime

from pydantic import EmailStr

from src.domain.aggregate_root import AggregateRoot, BaseCommand, BaseEvent


class UserCommand(BaseCommand):
    command_id: str
    timestamp: datetime

    # might need specification pattern here
    def validate(self) -> bool:
        return True


class UserEvent(BaseEvent):
    event_id: str
    timestamp: datetime


class User(AggregateRoot[BaseCommand, BaseEvent]):
    email: EmailStr
    is_active: bool = False
    full_name: str

    def process(self, command: BaseCommand) -> list[BaseEvent]:
        if command.validate():
            return []
        else:
            return []

    def apply(self, event: BaseEvent) -> None:
        pass
