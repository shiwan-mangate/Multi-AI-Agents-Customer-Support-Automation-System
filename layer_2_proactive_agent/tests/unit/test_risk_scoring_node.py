import pytest
from unittest.mock import patch

from layer_2_proactive_agent.nodes.risk_scoring_node import (
    risk_scoring_node,
)


# ---------------------------------------------------------
# Test 1: Happy Path (Successful Scoring)
# ---------------------------------------------------------

@patch(
    "layer_2_proactive_agent.nodes.risk_scoring_node"
    ".risk_engine.assess"
)
def test_risk_scoring_happy_path(
    mock_assess,
    sample_proactive_state,
    sample_risk_assessment,
):
    """
    Verifies the node extracts both required state inputs, 
    calls the risk engine, and attaches the resulting assessment.
    """
    
    state = sample_proactive_state.copy()
    state["risk_assessment"] = None
    
    mock_assess.return_value = sample_risk_assessment

    result = risk_scoring_node(
        state=state
    )

    mock_assess.assert_called_once_with(
        signal_assessment=state["signal_assessment"],
        customer_profile=state["customer_profile"],
    )
    
    assert result["current_node"] == "risk_scoring_node"
    assert result["risk_assessment"] == sample_risk_assessment
    assert len(result["workflow_logs"]) == 1


# ---------------------------------------------------------
# Test 2: Missing Signal Assessment (Corrupted State)
# ---------------------------------------------------------

def test_risk_scoring_missing_signal_assessment(
    sample_proactive_state,
):
    """
    If upstream state drops the signal_assessment, 
    the node must safely fail before executing the service.
    """
    
    state = sample_proactive_state.copy()
    state["signal_assessment"] = None

    with pytest.raises(
        ValueError, 
        match="Missing signal_assessment."
    ):
        risk_scoring_node(
            state=state
        )


# ---------------------------------------------------------
# Test 3: Missing Customer Profile (Corrupted State)
# ---------------------------------------------------------

def test_risk_scoring_missing_customer_profile(
    sample_proactive_state,
):
    """
    If the context node failed to hydrate the profile but 
    the graph continued, this node must catch the corruption.
    """
    
    state = sample_proactive_state.copy()
    state["customer_profile"] = None

    with pytest.raises(
        ValueError, 
        match="Missing customer_profile."
    ):
        risk_scoring_node(
            state=state
        )


# ---------------------------------------------------------
# Test 4: Engine Returns None (Safety Guard)
# ---------------------------------------------------------

@patch(
    "layer_2_proactive_agent.nodes.risk_scoring_node"
    ".risk_engine.assess"
)
def test_risk_scoring_engine_returns_none(
    mock_assess,
    sample_proactive_state,
):
    """
    If the RiskEngine unexpectedly fails to return an object, 
    the node must trap the None value and fail explicitly.
    """
    
    mock_assess.return_value = None

    with pytest.raises(
        ValueError, 
        match="Risk assessment failed."
    ):
        risk_scoring_node(
            state=sample_proactive_state
        )

    mock_assess.assert_called_once()


# ---------------------------------------------------------
# Test 5: Service Exception Handling
# ---------------------------------------------------------

@patch(
    "layer_2_proactive_agent.nodes.risk_scoring_node"
    ".risk_engine.assess"
)
def test_risk_scoring_service_error(
    mock_assess,
    sample_proactive_state,
):
    """
    If the underlying risk engine throws a calculation error, 
    the node must catch, log, and propagate it.
    """
    
    mock_assess.side_effect = Exception("Division by zero in risk score calculation")

    with pytest.raises(
        Exception, 
        match="Division by zero"
    ):
        risk_scoring_node(
            state=sample_proactive_state
        )
        
    mock_assess.assert_called_once()


# ---------------------------------------------------------
# Test 6: Verify Exact Object Propagation
# ---------------------------------------------------------

@patch(
    "layer_2_proactive_agent.nodes.risk_scoring_node"
    ".risk_engine.assess"
)
def test_risk_scoring_propagation(
    mock_assess,
    sample_proactive_state,
    sample_risk_assessment,
):
    """
    Ensures the exact Pydantic model returned by the engine
    is attached to the LangGraph state.
    """

    mock_assess.return_value = sample_risk_assessment

    result = risk_scoring_node(
        state=sample_proactive_state
    )

    assessment = result["risk_assessment"]

    assert result["current_node"] == "risk_scoring_node"
    assert assessment.risk_level == sample_risk_assessment.risk_level
    assert assessment.risk_score == sample_risk_assessment.risk_score
    assert assessment.escalation_candidate is sample_risk_assessment.escalation_candidate


# ---------------------------------------------------------
# Test 7: Log Message Format & Structure
# ---------------------------------------------------------

@patch(
    "layer_2_proactive_agent.nodes.risk_scoring_node"
    ".risk_engine.assess"
)
def test_risk_scoring_log_formatting(
    mock_assess,
    sample_proactive_state,
    sample_risk_assessment,
):
    """
    Validates that workflow logs correctly format the 
    enum value and decimal score.
    """

    mock_assess.return_value = sample_risk_assessment

    result = risk_scoring_node(
        state=sample_proactive_state
    )

    assert result["current_node"] == "risk_scoring_node"

    log = result["workflow_logs"][0]

    # Validate schema
    assert log["node"] == "risk_scoring_node"
    assert isinstance(log["timestamp"], str)

    # Validate exact string interpolation from the node
    assert f"level={sample_risk_assessment.risk_level.value}" in log["message"]
    assert f"score={sample_risk_assessment.risk_score}" in log["message"]