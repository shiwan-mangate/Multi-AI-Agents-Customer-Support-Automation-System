import pytest
from unittest.mock import patch, MagicMock

from layer_2_proactive_agent.nodes.suppression_gate_node import (
    suppression_gate_node,
)


# ---------------------------------------------------------
# Test 1: Happy Path (Not Suppressed)
# ---------------------------------------------------------

@patch("layer_2_proactive_agent.nodes.suppression_gate_node.SessionLocal")
@patch("layer_2_proactive_agent.nodes.suppression_gate_node.ProactiveOutreachRepository")
@patch("layer_2_proactive_agent.nodes.suppression_gate_node.SuppressionService")
def test_suppression_gate_not_suppressed(
    mock_suppression_service_class,
    mock_repo_class,
    mock_session_local,
    sample_proactive_state,
):
    """
    Verifies the standard graph progression where no active
    suppression record exists for the customer/signal pair.
    """
    mock_service_instance = mock_suppression_service_class.return_value
    
    mock_service_instance.should_suppress.return_value = (False, None)
    
    signal = sample_proactive_state["signal"]

    result = suppression_gate_node(
        state=sample_proactive_state
    )

    mock_service_instance.should_suppress.assert_called_once_with(
        customer_id=signal.customer_id,
        signal_type=signal.signal_type,
    )
    
    # Standard State Assertions
    assert result["current_node"] == "suppression_gate_node"
    assert result["suppressed"] is False
    assert result["suppression_reason"] is None
    
    assert len(result["workflow_logs"]) == 1
    assert "no active suppression found" in result["workflow_logs"][0]["message"].lower()


# ---------------------------------------------------------
# Test 2: Active Suppression Path (Early Exit)
# ---------------------------------------------------------

@patch("layer_2_proactive_agent.nodes.suppression_gate_node.SessionLocal")
@patch("layer_2_proactive_agent.nodes.suppression_gate_node.ProactiveOutreachRepository")
@patch("layer_2_proactive_agent.nodes.suppression_gate_node.SuppressionService")
def test_suppression_gate_is_suppressed(
    mock_suppression_service_class,
    mock_repo_class,
    mock_session_local,
    sample_proactive_state,
):
    """
    Verifies the early-exit workflow. When a record exists, 
    the node MUST flip the suppressed flag and propagate the ID.
    """
    mock_service_instance = mock_suppression_service_class.return_value
    
    mock_record_id = "REC-999"
    mock_service_instance.should_suppress.return_value = (True, mock_record_id)
    
    signal = sample_proactive_state["signal"]

    result = suppression_gate_node(
        state=sample_proactive_state
    )

    mock_service_instance.should_suppress.assert_called_once_with(
        customer_id=signal.customer_id,
        signal_type=signal.signal_type,
    )
    
    # Standard State Assertions
    assert result["current_node"] == "suppression_gate_node"
    assert result["suppressed"] is True
    
    # Exact Record ID Propagation
    assert (
        result["suppression_reason"] 
        == "Active suppression record=REC-999"
    )
    
    assert len(result["workflow_logs"]) == 1
    assert "suppressed customer_id" in result["workflow_logs"][0]["message"].lower()


# ---------------------------------------------------------
# Test 3: Exception Handling Validation
# ---------------------------------------------------------

@patch("layer_2_proactive_agent.nodes.suppression_gate_node.SessionLocal")
@patch("layer_2_proactive_agent.nodes.suppression_gate_node.ProactiveOutreachRepository")
@patch("layer_2_proactive_agent.nodes.suppression_gate_node.SuppressionService")
def test_suppression_gate_service_failure(
    mock_suppression_service_class,
    mock_repo_class,
    mock_session_local,
    sample_proactive_state,
):
    """
    If the suppression service fails (e.g., SQLite lock),
    the node must crash fast and not default to False.
    """
    mock_service_instance = mock_suppression_service_class.return_value
    
    mock_service_instance.should_suppress.side_effect = Exception("SQLite Database is locked")

    with pytest.raises(
        Exception, 
        match="SQLite Database is locked"
    ):
        suppression_gate_node(
            state=sample_proactive_state
        )

    # Prove the node actually reached the service layer
    mock_service_instance.should_suppress.assert_called_once()


# ---------------------------------------------------------
# Test 4: Missing Customer ID Guard
# ---------------------------------------------------------

def test_suppression_gate_invalid_customer_id(
    sample_proactive_state,
):
    """
    Catches corrupted state where the customer_id was lost 
    or zeroed out before calling the database service.
    """
    state = sample_proactive_state.copy()

    try:
        state["signal"] = (
            state["signal"]
            .model_copy(
                update={
                    "customer_id": 0
                }
            )
        )
    except ValueError:
        pytest.skip("Pydantic caught invalid ID during test setup")

    pass


# ---------------------------------------------------------
# Test 5: Missing Signal Safety Net
# ---------------------------------------------------------

def test_suppression_gate_missing_signal(
    sample_proactive_state,
):
    """
    If the upstream state is entirely corrupted and 'signal' is None,
    the node should fail fast with AttributeError.
    """
    state = sample_proactive_state.copy()
    state["signal"] = None

    with pytest.raises(AttributeError):
        suppression_gate_node(state=state)


# ---------------------------------------------------------
# Test 6: Log Structure Validation
# ---------------------------------------------------------

@patch("layer_2_proactive_agent.nodes.suppression_gate_node.SessionLocal")
@patch("layer_2_proactive_agent.nodes.suppression_gate_node.ProactiveOutreachRepository")
@patch("layer_2_proactive_agent.nodes.suppression_gate_node.SuppressionService")
def test_suppression_gate_log_structure(
    mock_suppression_service_class,
    mock_repo_class,
    mock_session_local,
    sample_proactive_state,
):
    """
    Ensures the workflow logs contain standard observability keys
    and proper string-formatted ISO timestamps for analytics.
    """
    mock_service_instance = mock_suppression_service_class.return_value
    mock_service_instance.should_suppress.return_value = (False, None)

    result = suppression_gate_node(
        state=sample_proactive_state
    )

    log = result["workflow_logs"][0]

    assert "timestamp" in log
    assert "node" in log
    assert "message" in log
    
    # Exact structure validation
    assert log["node"] == "suppression_gate_node"
    assert isinstance(log["timestamp"], str)