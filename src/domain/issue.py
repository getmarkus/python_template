from datetime import datetime
from enum import Enum
from typing import Optional

from src.domain.aggregate_root import AggregateRoot, BaseCommand, BaseEvent

# https://docs.github.com/en/rest/using-the-rest-api/github-event-types?apiVersion=2022-11-28#issuesevent
# https://docs.github.com/en/rest/using-the-rest-api/issue-event-types?apiVersion=2022-11-28
# https://docs.github.com/en/rest/issues/events?apiVersion=2022-11-28#get-an-issue-event
# https://docs.github.com/en/rest/issues/issues?apiVersion=2022-11-28#update-an-issue
# https://docs.github.com/en/rest/issues/timeline?apiVersion=2022-11-28
# https://github.blog/open-source/maintainers/metrics-for-issues-pull-requests-and-discussions/

class IssueState(Enum):
    OPEN = "OPEN"
    CLOSED = "CLOSED"

    @property
    def is_open(self):
        return self == IssueState.OPEN

class IssueStateTransition(Enum):
    COMPLETED = "COMPLETED"
    NOT_PLANNED = "NOT_PLANNED"
    REOPENED = "REOPENED"

class IssueEventType(Enum):
    OPENED = "OPENED"
    EDITED = "EDITED"
    CLOSED = "CLOSED"
    REOPENED = "REOPENED"
    ASSIGNED = "ASSIGNED"
    UNASSIGNED = "UNASSIGNED"
    LABLED = "LABLED"
    UNLABLED = "UNLABLED"

### Events ###
class IssueEvent(BaseEvent):
    event_id: str
    timestamp: datetime
    issue_number: int
    issue_state: IssueState
    issue_state_transition: IssueStateTransition
    issue_event_type: IssueEventType
    changes: dict[str, any]
    previous_title: str
    previous_body: str
    assignee: Optional[str]
    label: Optional[str]

    def __init__(
        self,
        event_id: str,
        timestamp: datetime,
        issue_number: int,
        issue_state: IssueState,
        issue_state_transition: IssueStateTransition,
        issue_event_type: IssueEventType,
        changes: dict[str, any],
        previous_title: str,
        previous_body: str,
        assignee: Optional[str] = None,
        label: Optional[str] = None
    ):
        super().__init__()
        self.event_id = event_id
        self.timestamp = timestamp
        self.issue_number = issue_number
        self.issue_state = issue_state
        self.issue_state_transition = issue_state_transition
        self.issue_event_type = issue_event_type
        self.changes = changes
        self.previous_title = previous_title
        self.previous_body = previous_body
        self.assignee = assignee
        self.label = label

## potential sub-events
# - connected
# - disconnected
# - converted_to_discussion
# - milestoned
# - demilestoned
# - locked
# - mentioned
# - marked_as_duplicate
# - unmarked_as_duplicate
# - pinned
# - unpinned
# - referenced
# - renamed
# - subscribed
# - transferred
# - unlocked
# - user_blocked
# - commented OR IssueCommentEvent

### Commands ###
class IssueCommand(BaseCommand):
    command_id: str
    timestamp: datetime
    issue_number: int

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