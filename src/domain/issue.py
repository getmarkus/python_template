from datetime import datetime
from enum import Enum

from src.domain.aggregate_root import AggregateRoot, BaseCommand, BaseEvent


class IssueState(Enum):
    OPEN = "OPEN"
    CLOSED = "CLOSED"
    IN_PROGRESS = "IN_PROGRESS"
    REOPENED = "REOPENED"
    RESOLVED = "RESOLVED"

    @property
    def is_open(self):
        return self == IssueState.OPEN

class IssueEventType(Enum):
    OPENED = "OPENED"
    CLOSED = "CLOSED"
    IN_PROGRESS = "IN_PROGRESS"
    REOPENED = "REOPENED"
    RESOLVED = "RESOLVED"

    @property
    def is_open(self):
        return self == IssueEventType.OPENED

### Events ###
class IssueEvent(BaseEvent):
    event_id: str
    timestamp: datetime
    issue_number: int
    issue_state: IssueState
    issue_event_type: IssueEventType

### Commands ###
class IssueCommand(BaseCommand):
    command_id: str
    timestamp: datetime
    issue_number: int
    issue_state: IssueState

    # might need specification pattern here
    def validate(self) -> bool:
        return True

### Entitites ###
class Issue(AggregateRoot):
    issue_number: int

    def process(self, command: BaseCommand) -> list[BaseEvent]:
        if command.validate():
            return []
        else:
            return []

    def apply(self, event: BaseEvent) -> None:
        pass

    # likely need a handler method here for 'domain' events and not aggregate events

### Exceptions ###

### Value Objects ###