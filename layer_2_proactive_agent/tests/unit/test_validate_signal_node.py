import pytest
from types import SimpleNamespace

from layer_2_proactive_agent.nodes.validate_signal_node import (
    validate_signal_node,
)

from layer_2_proactive_agent.schemas.enums import (
    SignalType,
)


# ---------------------------------------------------------
# Test 1: Happy Path
# ---------------------------------------------------------

def test_validate_signal_happy_path(
    sample_proactive_state,
):
    """
    Valid signal should pass validation successfully
    and append an initialization log.
    """
    
    result = validate_signal_node(
        state=sample_proactive_state
    )

    assert result["current_node"] == "validate_signal_node"
    assert len(result["workflow_logs"]) == 1
    assert "validated successfully" in result["workflow_logs"][0]["message"].lower()


def test_validate_signal_log_node_name(
    sample_proactive_state,
):
    """
    Validates that the workflow log accurately records 
    the executing node's name for downstream tracing.
    """
    
    result = validate_signal_node(
        state=sample_proactive_state
    )

    assert result["workflow_logs"][0]["node"] == "validate_signal_node"


# ---------------------------------------------------------
# Test 2: Missing Signal Payload
# ---------------------------------------------------------

def test_validate_signal_missing_payload(
    sample_proactive_state,
):
    """
    Workflow should fail immediately if the state 
    does not contain a 'signal' object.
    """
    
    state = sample_proactive_state.copy()
    state["signal"] = None

    with pytest.raises(
        ValueError, 
        match="Missing 'signal' payload"
    ):
        validate_signal_node(
            state=state
        )


# ---------------------------------------------------------
# Test 3: Signal ID Validation
# ---------------------------------------------------------

def test_validate_signal_missing_signal_id(
    sample_proactive_state,
):
    """
    Signal without a valid signal_id should fail.
    """
    
    state = sample_proactive_state.copy()
    
    state["signal"] = SimpleNamespace(
        signal_id="",
        customer_id=123,
        signal_type=SignalType.HIGH_CHURN_RISK,
    )

    with pytest.raises(
        ValueError, 
        match="signal_id"
    ):
        validate_signal_node(
            state=state
        )


def test_validate_signal_whitespace_signal_id(
    sample_proactive_state,
):
    """
    Signal with a blank/whitespace signal_id should fail.
    """
    
    state = sample_proactive_state.copy()
    
    state["signal"] = SimpleNamespace(
        signal_id="   ",
        customer_id=123,
        signal_type=SignalType.HIGH_CHURN_RISK,
    )

    with pytest.raises(
        ValueError, 
        match="signal_id"
    ):
        validate_signal_node(
            state=state
        )


# ---------------------------------------------------------
# Test 4: Customer ID Validation
# ---------------------------------------------------------

def test_validate_signal_zero_customer_id(
    sample_proactive_state,
):
    """
    Customer ID must be strictly positive. 
    Zero should fail.
    """
    
    state = sample_proactive_state.copy()
    
    state["signal"] = SimpleNamespace(
        signal_id="SIG-123",
        customer_id=0,
        signal_type=SignalType.HIGH_CHURN_RISK,
    )

    with pytest.raises(
        ValueError, 
        match="customer_id"
    ):
        validate_signal_node(
            state=state
        )


def test_validate_signal_negative_customer_id(
    sample_proactive_state,
):
    """
    Customer ID must be strictly positive. 
    Negative values should fail.
    """
    
    state = sample_proactive_state.copy()
    
    state["signal"] = SimpleNamespace(
        signal_id="SIG-123",
        customer_id=-1,
        signal_type=SignalType.HIGH_CHURN_RISK,
    )

    with pytest.raises(
        ValueError, 
        match="customer_id"
    ):
        validate_signal_node(
            state=state
        )


# ---------------------------------------------------------
# Test 5: Strict Typing Validation
# ---------------------------------------------------------

def test_validate_signal_invalid_signal_type(
    sample_proactive_state,
):
    """
    Enforces strict typing. A string instead of the 
    SignalType enum should fail immediately.
    """
    
    state = sample_proactive_state.copy()
    
    state["signal"] = SimpleNamespace(
        signal_id="SIG-123",
        customer_id=123,
        signal_type="STRING_NOT_ENUM",
    )

    with pytest.raises(
        ValueError, 
        match="signal_type"
    ):
        validate_signal_node(
            state=state
        )