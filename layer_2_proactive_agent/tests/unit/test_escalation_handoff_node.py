import pytest
from unittest.mock import patch, Mock

from layer_2_proactive_agent.nodes.escalation_handoff_node import (
    escalation_handoff_node,
)


@pytest.fixture
def mock_handoff_ticket():
    """
    Simulates the EscalationHandoff object returned by the service.
    """
    ticket = Mock()
    ticket.ticket_id = "ESC-TKT-9001"
    ticket.customer_id = 123
    ticket.initial_urgency = "urgent"
    return ticket


# ---------------------------------------------------------
# Test 1: Happy Path (Successful Handoff Creation)
# ---------------------------------------------------------

@patch(
    "layer_2_proactive_agent.nodes.escalation_handoff_node"
    ".escalation_service.handoff"
)
def test_escalation_handoff_happy_path(
    mock_handoff_service,
    sample_proactive_state,
    mock_handoff_ticket,
):
    """
    Verifies that the node extracts all necessary context objects, 
    calls the escalation service, and appends the handoff ticket.
    """
    state = sample_proactive_state.copy()
    state["escalation_handoff"] = None
    
    mock_handoff_service.return_value = mock_handoff_ticket

    result = escalation_handoff_node(state=state)

    mock_handoff_service.assert_called_once_with(
        workflow_id=state["workflow_id"],
        customer_profile=state["customer_profile"],
        signal_assessment=state["signal_assessment"],
        risk_assessment=state["risk_assessment"],
    )
    
    assert result["current_node"] == "escalation_handoff_node"
    assert result["escalation_handoff"] == mock_handoff_ticket
    assert len(result["workflow_logs"]) == 1


# ---------------------------------------------------------
# Test 2: Missing Customer Profile (Context Engine Validation)
# ---------------------------------------------------------

@patch(
    "layer_2_proactive_agent.nodes.escalation_handoff_node"
    ".escalation_service.handoff"
)
def test_escalation_handoff_missing_customer_profile(
    mock_handoff_service,
    sample_proactive_state,
):
    """
    Verifies the context-validation guard intercepts missing state contexts
    and fails fast before downstream dispatching logic runs.
    """
    state = sample_proactive_state.copy()
    state["customer_profile"] = None

    with pytest.raises(
        ValueError, 
        match="Missing required context for escalation handoff: customer_profile"
    ):
        escalation_handoff_node(state=state)


# ---------------------------------------------------------
# Test 3: Service Returns None (Defensive Guard)
# ---------------------------------------------------------

@patch(
    "layer_2_proactive_agent.nodes.escalation_handoff_node"
    ".escalation_service.handoff"
)
def test_escalation_handoff_returns_none(
    mock_handoff_service,
    sample_proactive_state,
):
    """
    If the escalation service fails to generate a ticket and yields None, 
    the node will encounter an AttributeError on downstream property resolution.
    """
    state = sample_proactive_state.copy()
    mock_handoff_service.return_value = None

    with pytest.raises(AttributeError):
        escalation_handoff_node(state=state)


# ---------------------------------------------------------
# Test 4: Service Exception Handling
# ---------------------------------------------------------

@patch(
    "layer_2_proactive_agent.nodes.escalation_handoff_node"
    ".escalation_service.handoff"
)
def test_escalation_handoff_service_error(
    mock_handoff_service,
    sample_proactive_state,
):
    """
    If the underlying ticketing service API fails (e.g., timeout),
    the node must catch, log, and propagate the exception.
    """
    mock_handoff_service.side_effect = Exception("Ticketing API Timeout")

    with pytest.raises(
        Exception, 
        match="Ticketing API Timeout"
    ):
        escalation_handoff_node(state=sample_proactive_state)


# ---------------------------------------------------------
# Test 5: Verify Exact Object Propagation
# ---------------------------------------------------------

@patch(
    "layer_2_proactive_agent.nodes.escalation_handoff_node"
    ".escalation_service.handoff"
)
def test_escalation_handoff_propagation(
    mock_handoff_service,
    sample_proactive_state,
    mock_handoff_ticket,
):
    """
    Ensures the exact object returned by the service
    is attached to the LangGraph state without mutation.
    """
    mock_handoff_service.return_value = mock_handoff_ticket

    result = escalation_handoff_node(state=sample_proactive_state)
    handoff = result["escalation_handoff"]

    assert result["current_node"] == "escalation_handoff_node"
    assert handoff.ticket_id == "ESC-TKT-9001"
    assert handoff.customer_id == 123
    assert handoff.initial_urgency == "urgent"


# ---------------------------------------------------------
# Test 6: Log Message Format & Structure
# ---------------------------------------------------------

@patch(
    "layer_2_proactive_agent.nodes.escalation_handoff_node"
    ".escalation_service.handoff"
)
def test_escalation_handoff_log_formatting(
    mock_handoff_service,
    sample_proactive_state,
    mock_handoff_ticket,
):
    """
    Validates that workflow logs correctly interpolate structural tokens 
    for observability dashboard collection platforms.
    """
    mock_handoff_service.return_value = mock_handoff_ticket

    result = escalation_handoff_node(state=sample_proactive_state)

    assert result["current_node"] == "escalation_handoff_node"
    log = result["workflow_logs"][0]

    assert log["node"] == "escalation_handoff_node"
    assert isinstance(log["timestamp"], str)
    
    # Matches the exact string format emitted by the updated persistence layout node
    assert log["message"] == "Escalation package created (Ticket: ESC-TKT-9001) and recorded in registry."


# ---------------------------------------------------------
# Test 7: Missing Dictionary Key (Corrupted State Guard)
# ---------------------------------------------------------

def test_escalation_handoff_missing_state_keys():
    """
    If the graph state is totally corrupted and required dictionary 
    keys are missing entirely, verify it fails fast with KeyError.
    """
    corrupted_state = {}

    with pytest.raises(KeyError):
        escalation_handoff_node(state=corrupted_state)