import pytest
from unittest.mock import patch

from layer_2_proactive_agent.nodes.outreach_decision_node import (
    outreach_decision_node,
)


# ---------------------------------------------------------
# Test 1: Happy Path (Successful Decision)
# ---------------------------------------------------------

@patch(
    "layer_2_proactive_agent.nodes.outreach_decision_node"
    ".decision_service.decide"
)
def test_outreach_decision_happy_path(
    mock_decide,
    sample_proactive_state,
    sample_outreach_decision,
):
    """
    Verifies the node successfully extracts the risk assessment, 
    calls the decision service, and appends the resulting decision.
    """
    
    state = sample_proactive_state.copy()
    state["decision"] = None
    
    mock_decide.return_value = sample_outreach_decision
    risk_assessment = state["risk_assessment"]

    result = outreach_decision_node(
        state=state
    )

    mock_decide.assert_called_once_with(
        risk_assessment=risk_assessment
    )
    
    assert result["current_node"] == "outreach_decision_node"
    assert result["decision"] == sample_outreach_decision
    assert len(result["workflow_logs"]) == 1


# ---------------------------------------------------------
# Test 2: Missing Risk Assessment (Corrupted State)
# ---------------------------------------------------------

def test_outreach_decision_missing_risk_assessment(
    sample_proactive_state,
):
    """
    If the upstream risk_scoring_node failed or state was corrupted, 
    the node must safely fail before executing the service.
    """
    
    state = sample_proactive_state.copy()
    state["risk_assessment"] = None

    with pytest.raises(
        ValueError, 
        match="Missing risk_assessment in state."
    ):
        outreach_decision_node(
            state=state
        )


# ---------------------------------------------------------
# Test 3: Service Exception Handling
# ---------------------------------------------------------

@patch(
    "layer_2_proactive_agent.nodes.outreach_decision_node"
    ".decision_service.decide"
)
def test_outreach_decision_service_error(
    mock_decide,
    sample_proactive_state,
):
    """
    If the underlying decision service throws an error, 
    the node must catch, log, and propagate it.
    """
    
    mock_decide.side_effect = Exception("Decision ruleset timeout")

    with pytest.raises(
        Exception, 
        match="Decision ruleset timeout"
    ):
        outreach_decision_node(
            state=sample_proactive_state
        )
        
    mock_decide.assert_called_once()


# ---------------------------------------------------------
# Test 4: Verify Exact Object Propagation
# ---------------------------------------------------------

@patch(
    "layer_2_proactive_agent.nodes.outreach_decision_node"
    ".decision_service.decide"
)
def test_outreach_decision_propagation(
    mock_decide,
    sample_proactive_state,
    sample_outreach_decision,
):
    """
    Ensures the exact Pydantic model returned by the service
    is attached to state, specifically verifying action values.
    """

    mock_decide.return_value = sample_outreach_decision

    result = outreach_decision_node(
        state=sample_proactive_state
    )

    decision = result["decision"]

    assert result["current_node"] == "outreach_decision_node"
    
    # Precise value propagation check
    assert decision.action == sample_outreach_decision.action
    assert decision.action.value == sample_outreach_decision.action.value
    assert decision.reason == sample_outreach_decision.reason
    assert decision.review_required is sample_outreach_decision.review_required


# ---------------------------------------------------------
# Test 5: Log Message Format & Structure
# ---------------------------------------------------------

@patch(
    "layer_2_proactive_agent.nodes.outreach_decision_node"
    ".decision_service.decide"
)
def test_outreach_decision_log_formatting(
    mock_decide,
    sample_proactive_state,
    sample_outreach_decision,
):
    """
    Validates that workflow logs correctly interpolate the 
    decision action enum and human-readable reason.
    """

    mock_decide.return_value = sample_outreach_decision

    result = outreach_decision_node(
        state=sample_proactive_state
    )

    log = result["workflow_logs"][0]

    assert log["node"] == "outreach_decision_node"
    assert isinstance(log["timestamp"], str)

    expected_message = (
        f"Decision reached: "
        f"{sample_outreach_decision.action.value} "
        f"({sample_outreach_decision.reason})"
    )
    assert log["message"] == expected_message


# ---------------------------------------------------------
# Test 6: Service Returns None (Defensive Fallback)
# ---------------------------------------------------------

@patch(
    "layer_2_proactive_agent.nodes.outreach_decision_node"
    ".decision_service.decide"
)
def test_outreach_decision_service_returns_none(
    mock_decide,
    sample_proactive_state,
):
    """
    Verifies that the node fails with AttributeError if the service 
    unexpectedly yields None, preventing null pointer propagation.
    """

    mock_decide.return_value = None

    with pytest.raises(
        AttributeError
    ):
        outreach_decision_node(
            state=sample_proactive_state
        )


# ---------------------------------------------------------
# Test 7: Verify Action Value Mapping
# ---------------------------------------------------------

@patch(
    "layer_2_proactive_agent.nodes.outreach_decision_node"
    ".decision_service.decide"
)
def test_outreach_decision_action_value_propagation(
    mock_decide,
    sample_proactive_state,
    sample_outreach_decision,
):
    """
    Ensures that the string value of the action is correctly propagated,
    as downstream routers depend exclusively on this mapping.
    """

    mock_decide.return_value = sample_outreach_decision

    result = outreach_decision_node(
        state=sample_proactive_state
    )

    assert result["decision"].action.value == sample_outreach_decision.action.value