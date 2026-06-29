import pytest
from unittest.mock import Mock, patch

from layer_2_proactive_agent.adapters.proactive_adapter import (
    ProactiveAdapter,
)

from layer_2_proactive_agent.schemas.enums import (
    OutreachStatus,
)


@pytest.fixture
def adapter():
    """Provides a fresh, stateless instance of the ProactiveAdapter."""
    return ProactiveAdapter()


def create_mock_output(status: OutreachStatus, full_context: bool = True):
    """
    Helper function to generate a precise Mock of the ProactiveOutput.
    Using Mocks avoids complex Pydantic validation for upstream models.
    """
    mock_out = Mock()
    mock_out.workflow_id = "WF-12345"
    mock_out.agent_id = "proactive_agent"
    mock_out.status = status
    mock_out.customer_id = 999

    if full_context:
        # Decision Mock (FIX 3: Ensure confidence is absent in actual use)
        mock_out.decision.reason = "Calculated risk warrants action."
        mock_out.decision.action.value = "OUTREACH"
        mock_out.decision.review_required = False

        # Risk & Signal Mocks
        mock_out.risk_assessment.risk_level.value = "HIGH"
        mock_out.signal_assessment.signal_type.value = "HIGH_CHURN_RISK"

        # Handoff Mock
        mock_out.escalation_handoff.ticket_id = "ESC-TKT-999"

        # Message Mock
        mock_out.outreach_message.channel = "email"
        mock_out.outreach_message.generated_by = "gpt-4-turbo"
        mock_out.outreach_message.subject = "Checking in"
        mock_out.outreach_message.body = "Hello from support!"
    else:
        # Simulate an early-exit or missing context state
        mock_out.decision = None
        mock_out.risk_assessment = None
        mock_out.signal_assessment = None
        mock_out.escalation_handoff = None
        mock_out.outreach_message = None

    return mock_out


# ---------------------------------------------------------
# Test 1: Suppressed Path
# ---------------------------------------------------------

@patch("layer_2_proactive_agent.adapters.proactive_adapter.uuid4")
def test_adapter_suppressed_path(mock_uuid, adapter):
    """
    Verifies the hardcoded mapping values when the workflow 
    was suppressed by the cooldown rules.
    """
    mock_uuid.return_value = "mocked-uuid-111"
    mock_out = create_mock_output(OutreachStatus.SUPPRESSED)

    event = adapter.to_crm_event(output=mock_out)

    assert event.resolution.status == "duplicate_suppressed"
    assert event.resolution.resolution_type == "proactive_suppression"
    assert event.resolution.resolution_message == "Suppressed by cooldown rules."
    assert event.resolution.resolved_by == "proactive_agent_suppression_engine"

    assert event.event.event_type == "ticket.resolved"
    assert event.event.event_id == "mocked-uuid-111"


# ---------------------------------------------------------
# Test 2: Escalation Path
# ---------------------------------------------------------

def test_adapter_escalation_path(adapter):
    """
    Verifies mapping when a human escalation is required.
    Should pull the explicit ticket ID from the handoff object.
    """
    mock_out = create_mock_output(OutreachStatus.ESCALATION_REQUIRED)

    event = adapter.to_crm_event(output=mock_out)

    assert event.event.event_type == "ticket.escalated"
    assert event.resolution.status == "escalated"
    assert event.resolution.resolution_type == "proactive_escalation"
    
    assert event.resolution.resolution_message == "Calculated risk warrants action."
    
    assert event.ticket.ticket_id == "ESC-TKT-999"
    assert event.risk.escalated is True


# ---------------------------------------------------------
# Test 3: Outreach Path (Message Generation)
# ---------------------------------------------------------

def test_adapter_outreach_path(adapter):
    """
    Verifies mapping when an LLM message was generated.
    Must correctly populate the ConversationMetadata array.
    """
    mock_out = create_mock_output(OutreachStatus.OUTREACH_CREATED)

    event = adapter.to_crm_event(output=mock_out)

    assert event.resolution.status == "resolved"
    assert event.resolution.resolution_type == "proactive_outreach"
    assert event.resolution.resolved_by == "gpt-4-turbo"
    assert event.ticket.channel == "email"

    assert event.conversation is not None
    assert len(event.conversation.messages) == 1
    msg = event.conversation.messages[0]
    
    assert msg["role"] == "assistant"
    assert msg["subject"] == "Checking in"
    assert msg["content"] == "Hello from support!"
    assert "proactive_agent" in event.conversation.agents_involved


# ---------------------------------------------------------
# Test 4: No Action Path
# ---------------------------------------------------------

def test_adapter_no_action_path(adapter):
    """
    Verifies standard resolution mappings when the agent determines
    the risk threshold is too low to bother the customer.
    """
    # FIX 1: Corrected to OutreachStatus.NO_ACTION
    mock_out = create_mock_output(OutreachStatus.NO_ACTION)
    
    mock_out.decision.reason = "Risk score is only 12."

    event = adapter.to_crm_event(output=mock_out)

    assert event.resolution.status == "resolved"
    assert event.resolution.resolution_type == "proactive_no_action"
    assert event.resolution.resolution_message == "Risk score is only 12."
    assert event.resolution.resolved_by == "proactive_agent_decision_engine"


# ---------------------------------------------------------
# Test 5: Fallback / Unknown Status Path
# ---------------------------------------------------------

def test_adapter_unknown_status_path(adapter):
    """
    Defensive test. If a new OutreachStatus is added to the enum but 
    forgotten in the adapter, it should map to a failed ticket state.
    """
    mock_out = create_mock_output("NEW_FUTURE_STATUS")

    event = adapter.to_crm_event(output=mock_out)

    assert event.event.event_type == "ticket.failed"
    assert event.resolution.status == "failed"
    assert event.resolution.resolution_type == "proactive_failure"
    assert event.resolution.resolution_message == "Unknown workflow status: NEW_FUTURE_STATUS"


# ---------------------------------------------------------
# Test 6: Missing Optional Context (Safety Net)
# ---------------------------------------------------------

def test_adapter_missing_optional_context(adapter):
    """
    Verifies the `else` fallbacks in the property accessors.
    If the graph exits early, risk, signal, and decision objects 
    may be None. The adapter must use safe default strings.
    """
    mock_out = create_mock_output(
        status=OutreachStatus.SUPPRESSED, 
        full_context=False
    )

    event = adapter.to_crm_event(output=mock_out)

    assert event.ticket.ticket_id == f"TKT-{mock_out.workflow_id}"
    assert event.ticket.channel == "system"
    
    assert event.risk.risk_level == "LOW"
    assert event.risk.human_review_required is False
    
    assert event.analytics.intent == "unknown_signal"
    
    assert event.conversation is None


# ---------------------------------------------------------
# Test 7: Exception Handling (Corrupted Input)
# ---------------------------------------------------------

def test_adapter_exception_handling(adapter):
    """
    Ensures that if adaptation critically fails, the exception 
    is caught, logged, and re-raised exactly as-is.
    """
    corrupted_output = object()

    with pytest.raises(AttributeError):
        adapter.to_crm_event(output=corrupted_output)