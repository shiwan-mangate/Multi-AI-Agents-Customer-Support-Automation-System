import pytest

from decimal import Decimal

from layer_2_proactive_agent.adapters.proactive_adapter import (
    ProactiveAdapter,
)

from layer_2_proactive_agent.schemas.proactive_output import (
    ProactiveOutput,
)

from layer_2_proactive_agent.schemas.enums import (
    OutreachStatus,
    OutreachAction,
    RiskLevel,
    SignalType,
)

from layer_2_proactive_agent.schemas.outreach_decision import (
    OutreachDecision,
)

from layer_2_proactive_agent.schemas.risk_assessment import (
    RiskAssessment,
)

from layer_2_proactive_agent.schemas.signal_assessment import (
    SignalAssessment,
)

from layer_2_proactive_agent.schemas.outreach_message import (
    OutreachMessage,
)

from layer_2_proactive_agent.schemas.escalation_handoff import (
    EscalationHandoff,
)

from crm_agent.schemas.crm_event import (
    CRMResolvedEvent,
)


@pytest.fixture
def adapter():
    return ProactiveAdapter()


# ---------------------------------------------------------
# Helper Factory
# ---------------------------------------------------------

def build_output(
    status: OutreachStatus,
) -> ProactiveOutput:

    signal = SignalAssessment(
        signal_type=SignalType.HIGH_CHURN_RISK,
        severity=RiskLevel.HIGH,
        detected_reason="High churn probability",
        requires_immediate_attention=True,
    )

    risk = RiskAssessment(
        risk_level=RiskLevel.HIGH,
        risk_score=Decimal("85.50"),
        risk_reasons=["High churn score"],
        escalation_candidate=False,
    )

    decision = OutreachDecision(
        action=OutreachAction.OUTREACH,
        reason="Customer requires outreach",
        review_required=False,
    )

    outreach_message = None
    escalation_handoff = None

    if status == OutreachStatus.OUTREACH_CREATED:

        outreach_message = OutreachMessage(
            subject="Checking In",
            body="Hello customer",
            channel="email",
            generated_by="gpt-4o",
        )

    elif status == OutreachStatus.ESCALATION_REQUIRED:

        decision = OutreachDecision(
            action=OutreachAction.ESCALATE,
            reason="Critical customer",
            review_required=True,
        )

        escalation_handoff = EscalationHandoff(
            ticket_id="ESC-001",
            customer_id=123,
            customer_email="test@example.com",
            initial_intent="HIGH_CHURN_RISK",
            initial_sentiment="negative",
            initial_urgency="urgent",
            message_raw="Escalation",
            message_english="Escalation",
        )

    elif status == OutreachStatus.SUPPRESSED:

        signal = None
        risk = None
        decision = None

    elif status == OutreachStatus.NO_ACTION:

        decision = OutreachDecision(
            action=OutreachAction.NO_ACTION,
            reason="Risk below threshold",
            review_required=False,
        )

    return ProactiveOutput(
        workflow_id="WF-001",
        status=status,
        customer_id=123,
        signal_assessment=signal,
        risk_assessment=risk,
        decision=decision,
        outreach_message=outreach_message,
        escalation_handoff=escalation_handoff,
    )


# ---------------------------------------------------------
# Test 1
# OUTREACH_CREATED
# ---------------------------------------------------------

def test_create_outreach_crm_event(
    adapter,
):

    output = build_output(
        OutreachStatus.OUTREACH_CREATED
    )

    crm_event = adapter.to_crm_event(output)

    assert isinstance(
        crm_event,
        CRMResolvedEvent,
    )

    assert crm_event.resolution.status == "resolved"

    assert (
        crm_event.resolution.resolution_type
        == "proactive_outreach"
    )

    assert (
        crm_event.ticket.channel
        == "email"
    )

    assert (
        crm_event.analytics.intent
        == "HIGH_CHURN_RISK"
    )

    assert (
        crm_event.risk.risk_level
        == "HIGH"
    )

    assert crm_event.conversation is not None


# ---------------------------------------------------------
# Test 2
# ESCALATION_REQUIRED
# ---------------------------------------------------------

def test_create_escalation_crm_event(
    adapter,
):

    output = build_output(
        OutreachStatus.ESCALATION_REQUIRED
    )

    crm_event = adapter.to_crm_event(output)

    assert (
        crm_event.resolution.status
        == "escalated"
    )

    assert (
        crm_event.resolution.resolution_type
        == "proactive_escalation"
    )

    assert (
        crm_event.ticket.ticket_id
        == "ESC-001"
    )

    assert crm_event.risk.escalated is True

    assert crm_event.conversation is None


# ---------------------------------------------------------
# Test 3
# SUPPRESSED
# ---------------------------------------------------------

def test_create_suppressed_crm_event(
    adapter,
):

    output = build_output(
        OutreachStatus.SUPPRESSED
    )

    crm_event = adapter.to_crm_event(output)

    assert (
        crm_event.resolution.status
        == "duplicate_suppressed"
    )

    assert (
        crm_event.resolution.resolution_type
        == "proactive_suppression"
    )

    assert (
        crm_event.analytics.intent
        == "unknown_signal"
    )

    assert (
        crm_event.risk.risk_level
        == "LOW"
    )

    assert (
        crm_event.ticket.ticket_id
        == "TKT-WF-001"
    )


# ---------------------------------------------------------
# Test 4
# NO_ACTION
# ---------------------------------------------------------

def test_create_no_action_crm_event(
    adapter,
):

    output = build_output(
        OutreachStatus.NO_ACTION
    )

    crm_event = adapter.to_crm_event(output)

    assert (
        crm_event.resolution.status
        == "resolved"
    )

    assert (
        crm_event.resolution.resolution_type
        == "proactive_no_action"
    )


# ---------------------------------------------------------
# Test 5
# JSON Serialization
# ---------------------------------------------------------

def test_crm_event_json_serialization(
    adapter,
):

    output = build_output(
        OutreachStatus.OUTREACH_CREATED
    )

    crm_event = adapter.to_crm_event(output)

    payload = (
        crm_event.model_dump_json()
    )

    assert isinstance(
        payload,
        str,
    )

    assert (
        "proactive_outreach"
        in payload
    )

    assert (
        "Checking In"
        in payload
    )