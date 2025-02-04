import pytest

from app.domain.issue import IssueState, IssueTransitionType


def test_initial_state():
    """Test that initial states are created correctly"""
    assert IssueState.OPEN.value == "OPEN"
    assert IssueState.CLOSED.value == "CLOSED"

def test_is_open_property():
    """Test the is_open property returns correct values"""
    assert IssueState.OPEN.is_open is True
    assert IssueState.CLOSED.is_open is False

def test_valid_transitions():
    """Test all valid state transitions"""
    # Test closing an open issue
    state = IssueState.OPEN
    new_state = state.transition(IssueTransitionType.CLOSE_AS_COMPLETE)
    assert new_state == IssueState.CLOSED

    state = IssueState.OPEN
    new_state = state.transition(IssueTransitionType.CLOSE_AS_NOT_PLANNED)
    assert new_state == IssueState.CLOSED

    # Test reopening a closed issue
    state = IssueState.CLOSED
    new_state = state.transition(IssueTransitionType.REOPEN)
    assert new_state == IssueState.OPEN

def test_invalid_transitions():
    """Test that invalid transitions raise appropriate errors"""
    # Test cannot close an already closed issue
    with pytest.raises(ValueError) as exc_info:
        IssueState.CLOSED.transition(IssueTransitionType.CLOSE_AS_COMPLETE)
    assert "Cannot perform CLOSE_AS_COMPLETE transition from state CLOSED" in str(
        exc_info.value
    )

    # Test cannot reopen an already open issue
    with pytest.raises(ValueError) as exc_info:
        IssueState.OPEN.transition(IssueTransitionType.REOPEN)
    assert "Cannot perform REOPEN transition from state OPEN" in str(exc_info.value)

def test_unknown_transition_type():
    """Test that using an undefined transition type raises an error"""

    # Create a new enum value that isn't in the transitions dictionary
    class FakeTransitionType:
        def __str__(self):
            return "FAKE_TRANSITION"

    with pytest.raises(ValueError) as exc_info:
        IssueState.OPEN.transition(FakeTransitionType())
    assert "Unknown transition type: FAKE_TRANSITION" in str(exc_info.value)

def test_transitions_immutability():
    """Test that the transitions dictionary cannot be modified at runtime"""
    transitions = IssueState.transitions()
    with pytest.raises((TypeError, AttributeError)):
        transitions[IssueTransitionType.REOPEN] = {
            "from": IssueState.OPEN.value,
            "to": IssueState.CLOSED.value,
        }
