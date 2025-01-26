from dataclasses import dataclass
from datetime import datetime
from enum import Enum, auto
from types import MappingProxyType
from typing import Any, Final, Optional

from src.domain.aggregate_root import AggregateRoot, BaseCommand, BaseEvent

# https://docs.github.com/en/rest/using-the-rest-api/github-event-types?apiVersion=2022-11-28#issuesevent
# https://docs.github.com/en/rest/using-the-rest-api/issue-event-types?apiVersion=2022-11-28
# https://docs.github.com/en/rest/issues/events?apiVersion=2022-11-28#get-an-issue-event
# https://docs.github.com/en/rest/issues/issues?apiVersion=2022-11-28#update-an-issue
# https://docs.github.com/en/rest/issues/timeline?apiVersion=2022-11-28
# https://github.blog/open-source/maintainers/metrics-for-issues-pull-requests-and-discussions/

### Enums ###

class IssueTransitionState(Enum):
    COMPLETED = "COMPLETED"
    NOT_PLANNED = "NOT_PLANNED"
    REOPENED = "REOPENED"


class IssueTransitionType(Enum):
    CLOSE_AS_COMPLETE = auto()
    CLOSE_AS_NOT_PLANNED = auto()
    REOPEN = auto()


class IssueEventType(Enum):
    OPENED = "OPENED"
    EDITED = "EDITED"
    CLOSED = "CLOSED"
    REOPENED = "REOPENED"
    ASSIGNED = "ASSIGNED"
    UNASSIGNED = "UNASSIGNED"
    LABLED = "LABLED"
    UNLABLED = "UNLABLED"


# https://github.com/pytransitions/transitions?tab=readme-ov-file#transitions
# https://python-statemachine.readthedocs.io/en/latest/auto_examples/persistent_model_machine.html
# important features of state machines:
# States, Transistions, Events, Actions(state, transition), Conditions, Validators (guard), Listeners
# State Actions: on_enter, on_exit
# Transition Actions: before, on, after


@dataclass(frozen=True)
class StateTransition:
    """Represents a valid transition between states"""

    from_state: "IssueState"
    to_state: "IssueState"


class IssueState(Enum):
    OPEN = "OPEN"
    CLOSED = "CLOSED"

    @classmethod
    def transitions(cls) -> dict[IssueTransitionType, StateTransition]:
        """Get the valid state transitions"""
        return _ISSUE_STATE_TRANSITIONS

    @property
    def is_open(self) -> bool:
        return self == IssueState.OPEN

    def transition(self, transition_type: IssueTransitionType) -> "IssueState":
        """
        Change the state based on the given transition type, enforcing valid transitions.
        Args:
            transition_type: The type of transition to perform
        Returns:
            The new IssueState after the transition
        Raises:
            ValueError: If the transition is not valid for the current state
        """
        if not isinstance(transition_type, IssueTransitionType):
            raise ValueError(f"Unknown transition type: {transition_type}")

        try:
            transition = self.transitions()[transition_type]
        except KeyError as err:
            raise ValueError(f"Unknown transition type: {transition_type}") from err

        if self != transition.from_state:
            raise ValueError(
                f"Cannot perform {transition_type.name} transition from state {self.value}"
            )

        return transition.to_state


# Define valid transitions using the type-safe StateTransition class
_ISSUE_STATE_TRANSITIONS: Final[dict[IssueTransitionType, StateTransition]] = (
    MappingProxyType(
        {
            IssueTransitionType.CLOSE_AS_COMPLETE: StateTransition(
                IssueState.OPEN, IssueState.CLOSED
            ),
            IssueTransitionType.CLOSE_AS_NOT_PLANNED: StateTransition(
                IssueState.OPEN, IssueState.CLOSED
            ),
            IssueTransitionType.REOPEN: StateTransition(
                IssueState.CLOSED, IssueState.OPEN
            ),
        }
    )
)


### Exceptions ###

### Value Objects ###


### Events ###
class IssueEvent(BaseEvent):
    event_id: str
    timestamp: datetime
    issue_number: int
    issue_state: IssueState
    issue_state_transition: IssueTransitionState
    issue_event_type: IssueEventType
    changes: dict[str, Any]
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
        issue_state_transition: IssueTransitionState,
        issue_event_type: IssueEventType,
        changes: dict[str, Any],
        previous_title: str,
        previous_body: str,
        assignee: Optional[str] = None,
        label: Optional[str] = None,
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


### Entitites ###
class Issue(AggregateRoot):
    issue_number: int
    issue_state: IssueState = IssueState.OPEN

    def process(self, command: BaseCommand) -> list[BaseEvent]:
        if command.validate():
            return []
        else:
            return []

    def apply(self, event: BaseEvent) -> None:
        pass

    # likely need a handler method here for 'domain' events and not aggregate events


### Commands ###
class IssueCommand(BaseCommand):
    command_id: str
    timestamp: datetime
    issue: Issue

    # might need specification pattern here
    def validate(self) -> bool:
        return True
