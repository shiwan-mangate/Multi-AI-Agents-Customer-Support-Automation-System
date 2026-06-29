import pytest
from unittest.mock import Mock

from layer_2_proactive_agent.nodes.response_node import (
    response_node,
)
from layer_2_proactive_agent.schemas.proactive_output import (
    ProactiveOutput,
)
from layer_2_proactive_agent.schemas.enums import (
    OutreachStatus,
    OutreachAction,
)


# ---------------------------------------------------------
# Test 1: Happy Path - Outreach Created
# ---------------------------------------------------------
def test_response_node_outreach_created(sample_proactive_state):
    state = sample_proactive_state.copy()
    customer_id = state["signal"].customer_id
    
    result = response_node(state=state)

    assert result["current_node"] == "response_node"
    
    output = result["output"]
    assert isinstance(output, ProactiveOutput)
    assert output.status == OutreachStatus.OUTREACH_CREATED
    assert output.customer_id == customer_id
    
    assert output.decision == state["decision"]
    assert output.outreach_message == state["outreach_message"]


# ---------------------------------------------------------
# Test 2: Happy Path - Escalation Required
# ---------------------------------------------------------
def test_response_node_escalation_required(sample_proactive_state):
    state = sample_proactive_state.copy()
    
    state["decision"] = state["decision"].model_copy(
        update={"action": OutreachAction.ESCALATE}
    )

    result = response_node(state=state)
    output = result["output"]
    assert output.status == OutreachStatus.ESCALATION_REQUIRED


# ---------------------------------------------------------
# Test 3: Happy Path - No Action Required
# ---------------------------------------------------------
def test_response_node_no_action_required(sample_proactive_state):
    state = sample_proactive_state.copy()
    
    state["decision"] = state["decision"].model_copy(
        update={"action": OutreachAction.NO_ACTION}
    )

    result = response_node(state=state)
    output = result["output"]
    assert output.status == OutreachStatus.NO_ACTION


# ---------------------------------------------------------
# Test 4: Early Exit - Suppressed Workflow
# ---------------------------------------------------------
def test_response_node_suppressed_workflow(sample_proactive_state):
    state = sample_proactive_state.copy()
    state["suppressed"] = True
    
    state["decision"] = state["decision"].model_copy(
        update={"action": OutreachAction.OUTREACH}
    )

    result = response_node(state=state)
    output = result["output"]
    assert output.status == OutreachStatus.SUPPRESSED


# ---------------------------------------------------------
# Test 5: Validation Guard - Unable to Determine Status
# ---------------------------------------------------------
def test_response_node_indeterminate_status(sample_proactive_state):
    state = sample_proactive_state.copy()
    state["suppressed"] = False
    state["decision"] = None

    with pytest.raises(ValueError, match="Unable to determine OutreachStatus"):
        response_node(state=state)


# ---------------------------------------------------------
# Test 6: Fallback Logic - Missing Signal / Customer ID
# ---------------------------------------------------------
def test_response_node_missing_signal_fallback(sample_proactive_state):
    state = sample_proactive_state.copy()
    state["signal"] = None

    result = response_node(state=state)
    output = result["output"]
    assert output.customer_id == -1


# ---------------------------------------------------------
# Test 7: Object Propagation Integrity
# ---------------------------------------------------------
def test_response_node_object_propagation(sample_proactive_state):
    state = sample_proactive_state.copy()
    
    result = response_node(state=state)
    output = result["output"]
    
    assert output.workflow_id == state["workflow_id"]
    assert output.agent_id == "proactive_agent"
    assert output.signal_assessment == state["signal_assessment"]
    assert output.risk_assessment == state["risk_assessment"]
    assert output.decision == state["decision"]


# ---------------------------------------------------------
# Test 8: Log Formatting & Structure
# ---------------------------------------------------------
def test_response_node_log_formatting(sample_proactive_state):
    state = sample_proactive_state.copy()
    customer_id = state["signal"].customer_id

    result = response_node(state=state)
    log = result["workflow_logs"][0]

    assert log["node"] == "response_node"
    assert isinstance(log["timestamp"], str)

    expected_message = (
        f"Workflow completed for "
        f"customer={customer_id} with "
        f"status={OutreachStatus.OUTREACH_CREATED.value}"
    )
    assert log["message"] == expected_message


# ---------------------------------------------------------
# Test 9: Missing Workflow ID Guard
# ---------------------------------------------------------
def test_response_node_missing_workflow_id():
    with pytest.raises(KeyError):
        response_node({})