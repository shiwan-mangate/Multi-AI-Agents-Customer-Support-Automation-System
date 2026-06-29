import pytest
from unittest.mock import patch, MagicMock

from layer_2_proactive_agent.nodes.message_generation_node import (
    message_generation_node,
)


# ---------------------------------------------------------
# Test 1: Happy Path (Successful Generation)
# ---------------------------------------------------------

@patch("layer_2_proactive_agent.nodes.message_generation_node.SessionLocal")
@patch(
    "layer_2_proactive_agent.nodes.message_generation_node"
    ".message_generation_service.generate"
)
def test_message_generation_happy_path(
    mock_generate,
    mock_session_local,
    sample_proactive_state,
    sample_outreach_message,
):
    """
    Verifies that the node gathers all required context objects, 
    calls the generation service, handles DB context safety, and updates the state.
    """
    state = sample_proactive_state.copy()
    state["outreach_message"] = None
    
    mock_generate.return_value = sample_outreach_message

    # Setup database transaction mock contexts safely
    mock_db = MagicMock()
    mock_session_local.return_value.__enter__.return_value = mock_db

    result = message_generation_node(state=state)

    mock_generate.assert_called_once_with(
        customer_profile=state["customer_profile"],
        risk_assessment=state["risk_assessment"],
        signal_assessment=state["signal_assessment"],
    )
    
    assert result["current_node"] == "message_generation_node"
    assert result["outreach_message"] == sample_outreach_message
    assert len(result["workflow_logs"]) == 1


# ---------------------------------------------------------
# Test 2: Missing Context Validation (Combined)
# ---------------------------------------------------------

def test_message_generation_missing_all_context(
    sample_proactive_state,
):
    """
    Validates the specific error message logic when multiple 
    required objects are missing from the state.
    """
    state = sample_proactive_state.copy()
    state["customer_profile"] = None
    state["risk_assessment"] = None
    state["signal_assessment"] = None
    state["decision"] = None

    with pytest.raises(
        ValueError, 
        match="customer_profile, risk_assessment, signal_assessment, decision"
    ):
        message_generation_node(state=state)


# ---------------------------------------------------------
# Test 3: Missing Specific Context (Signal Only)
# ---------------------------------------------------------

def test_message_generation_missing_signal_assessment(
    sample_proactive_state,
):
    """
    Ensures that if the signal assessment is missing, 
    generation is blocked with a targeted error message.
    """
    state = sample_proactive_state.copy()
    state["signal_assessment"] = None

    with pytest.raises(
        ValueError, 
        match="Missing required context for message generation: signal_assessment"
    ):
        message_generation_node(state=state)


# ---------------------------------------------------------
# Test 4: Missing Specific Context (Profile Only)
# ---------------------------------------------------------

def test_message_generation_missing_customer_profile(
    sample_proactive_state,
):
    """
    Ensures that if the customer profile is missing, 
    generation is blocked with a targeted error message.
    """
    state = sample_proactive_state.copy()
    state["customer_profile"] = None

    with pytest.raises(
        ValueError,
        match="customer_profile"
    ):
        message_generation_node(state=state)


# ---------------------------------------------------------
# Test 5: LLM Service Exception
# ---------------------------------------------------------

@patch("layer_2_proactive_agent.nodes.message_generation_node.SessionLocal")
@patch(
    "layer_2_proactive_agent.nodes.message_generation_node"
    ".message_generation_service.generate"
)
def test_message_generation_service_error(
    mock_generate,
    mock_session_local,
    sample_proactive_state,
):
    """
    If the LLM layer or prompt service fails (e.g., API Timeout),
    the node must propagate the exception.
    """
    mock_generate.side_effect = Exception("LLM Provider unreachable")

    with pytest.raises(
        Exception, 
        match="LLM Provider unreachable"
    ):
        message_generation_node(state=sample_proactive_state)
        
    mock_generate.assert_called_once()


# ---------------------------------------------------------
# Test 6: Service Returns None (Defensive Guard)
# ---------------------------------------------------------

@patch("layer_2_proactive_agent.nodes.message_generation_node.SessionLocal")
@patch(
    "layer_2_proactive_agent.nodes.message_generation_node"
    ".message_generation_service.generate"
)
def test_message_generation_service_returns_none(
    mock_generate,
    mock_session_local,
    sample_proactive_state,
):
    """
    Defensive test.
    Service must return an OutreachMessage. If it yields None,
    the node must crash predictably at the attribute access layer.
    """
    mock_generate.return_value = None

    with pytest.raises(
        AttributeError
    ):
        message_generation_node(
            state=sample_proactive_state
        )


# ---------------------------------------------------------
# Test 7: Log Message Format & Node Identity
# ---------------------------------------------------------

@patch("layer_2_proactive_agent.nodes.message_generation_node.SessionLocal")
@patch(
    "layer_2_proactive_agent.nodes.message_generation_node"
    ".message_generation_service.generate"
)
def test_message_generation_log_message_exact(
    mock_generate,
    mock_session_local,
    sample_proactive_state,
    sample_outreach_message,
):
    """
    Ensures observability contract: current_node is correct,
    logs use proper ISO timestamps, and exact string formatting matches expectations.
    """
    mock_generate.return_value = sample_outreach_message

    mock_db = MagicMock()
    mock_session_local.return_value.__enter__.return_value = mock_db

    result = message_generation_node(state=sample_proactive_state)

    assert result["current_node"] == "message_generation_node"
    
    log = result["workflow_logs"][0]
    assert log["node"] == "message_generation_node"
    assert isinstance(log["timestamp"], str)

    # Verifies the exact message logging string format layout
    assert log["message"] == f"Generated outreach message via {sample_outreach_message.generated_by} for channel={sample_outreach_message.channel} and recorded in registry."