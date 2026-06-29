import pytest
from unittest.mock import patch

from layer_2_proactive_agent.nodes.signal_analysis_node import (
    signal_analysis_node,
)


# ---------------------------------------------------------
# Test 1: Happy Path (Successful Analysis)
# ---------------------------------------------------------

@patch(
    "layer_2_proactive_agent.nodes.signal_analysis_node"
    ".signal_detection_service.analyze"
)
def test_signal_analysis_happy_path(
    mock_analyze,
    sample_proactive_state,
    sample_signal_assessment,
):
    """
    Verifies the node successfully extracts the signal, 
    calls the analysis service, and updates the state.
    """
    
    state = sample_proactive_state.copy()
    state["signal_assessment"] = None
    
    mock_analyze.return_value = sample_signal_assessment
    signal = state["signal"]

    result = signal_analysis_node(
        state=state
    )

    mock_analyze.assert_called_once_with(
        signal=signal
    )
    
    assert result["current_node"] == "signal_analysis_node"
    assert result["signal_assessment"] is not None


# ---------------------------------------------------------
# Test 2: Service Returns None (Safety Guard)
# ---------------------------------------------------------

@patch(
    "layer_2_proactive_agent.nodes.signal_analysis_node"
    ".signal_detection_service.analyze"
)
def test_signal_analysis_returns_none(
    mock_analyze,
    sample_proactive_state,
):
    """
    If the service unexpectedly returns None, the node 
    must raise a ValueError instead of silently continuing.
    """
    
    mock_analyze.return_value = None

    with pytest.raises(
        ValueError, 
        match="Signal analysis failed."
    ):
        signal_analysis_node(
            state=sample_proactive_state
        )

    mock_analyze.assert_called_once()


# ---------------------------------------------------------
# Test 3: Service Exception Handling
# ---------------------------------------------------------

@patch(
    "layer_2_proactive_agent.nodes.signal_analysis_node"
    ".signal_detection_service.analyze"
)
def test_signal_analysis_service_error(
    mock_analyze,
    sample_proactive_state,
):
    """
    If the underlying service throws an exception, 
    the node must propagate it to fail the workflow.
    """
    
    mock_analyze.side_effect = Exception("Heuristics Engine Timeout")

    with pytest.raises(
        Exception, 
        match="Heuristics Engine Timeout"
    ):
        signal_analysis_node(
            state=sample_proactive_state
        )
        
    mock_analyze.assert_called_once()


# ---------------------------------------------------------
# Test 4: Missing Signal in State (Corrupted State)
# ---------------------------------------------------------

def test_signal_analysis_missing_signal(
    sample_proactive_state,
):
    """
    If upstream state is corrupted and 'signal' is None,
    the node fails early during initial logging (AttributeError).
    """
    
    state = sample_proactive_state.copy()
    state["signal"] = None

    with pytest.raises(
        AttributeError
    ):
        signal_analysis_node(
            state=state
        )


# ---------------------------------------------------------
# Test 5: Log Structure Validation
# ---------------------------------------------------------

@patch(
    "layer_2_proactive_agent.nodes.signal_analysis_node"
    ".signal_detection_service.analyze"
)
def test_signal_analysis_log_structure(
    mock_analyze,
    sample_proactive_state,
    sample_signal_assessment,
):
    """
    Ensures the workflow logs contain standard observability keys
    and proper string-formatted ISO timestamps for analytics.
    """
    
    mock_analyze.return_value = sample_signal_assessment

    result = signal_analysis_node(
        state=sample_proactive_state
    )

    log = result["workflow_logs"][0]

    assert "timestamp" in log
    assert "node" in log
    assert "message" in log
    
    assert log["node"] == "signal_analysis_node"
    assert isinstance(log["timestamp"], str)


# ---------------------------------------------------------
# Test 6: Verify Severity Propagation
# ---------------------------------------------------------

@patch(
    "layer_2_proactive_agent.nodes.signal_analysis_node"
    ".signal_detection_service.analyze"
)
def test_signal_analysis_severity_propagation(
    mock_analyze,
    sample_proactive_state,
    sample_signal_assessment,
):
    """
    Ensures the exact assessment object returned
    by the service is propagated into state.
    """

    mock_analyze.return_value = sample_signal_assessment

    result = signal_analysis_node(
        state=sample_proactive_state
    )

    assessment = result["signal_assessment"]

    assert assessment.severity == sample_signal_assessment.severity
    assert assessment.signal_type == sample_signal_assessment.signal_type


# ---------------------------------------------------------
# Test 7: Verify Workflow Log Message Format
# ---------------------------------------------------------

@patch(
    "layer_2_proactive_agent.nodes.signal_analysis_node"
    ".signal_detection_service.analyze"
)
def test_signal_analysis_log_message(
    mock_analyze,
    sample_proactive_state,
    sample_signal_assessment,
):
    """
    Ensures severity information is explicitly
    recorded in workflow logs.
    """

    mock_analyze.return_value = sample_signal_assessment

    result = signal_analysis_node(
        state=sample_proactive_state
    )

    log = result["workflow_logs"][0]

    # Directly tests the f-string output format
    assert "severity=HIGH" in log["message"]