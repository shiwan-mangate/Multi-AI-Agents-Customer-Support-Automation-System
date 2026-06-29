import pytest
from decimal import Decimal
from datetime import datetime, UTC
from unittest.mock import MagicMock

from layer_2_proactive_agent.services.escalation_service import EscalationService
from layer_2_proactive_agent.schemas.escalation_handoff import EscalationHandoff
from layer_2_proactive_agent.schemas.enums import RiskLevel, SignalType
from layer_2_proactive_agent.schemas.signal_assessment import SignalAssessment
from layer_2_proactive_agent.schemas.risk_assessment import RiskAssessment


# ==============================================================================
# FIXTURES & MOCKS
# ==============================================================================

@pytest.fixture
def escalation_service():
    return EscalationService()


@pytest.fixture
def mock_customer_profile():
    """
    Mocks the CRM CustomerProfile object passed from the customer_context_node.
    """
    profile = MagicMock()
    profile.customer_id = 999
    profile.customer_email = "urgent.customer@example.com"
    profile.tier = "enterprise"
    profile.ltv = Decimal("15000.50")
    
    # FIX: Matching the actual flattened CRM Database Model
    profile.last_sentiment = "furious"
    
    return profile


@pytest.fixture
def sample_signal_assessment():
    return SignalAssessment(
        signal_type=SignalType.HIGH_CHURN_RISK,
        severity=RiskLevel.CRITICAL,
        detected_reason="Usage dropped by 90% in 3 days.",
        requires_immediate_attention=True,
    )


@pytest.fixture
def sample_risk_assessment():
    return RiskAssessment(
        risk_level=RiskLevel.CRITICAL,
        risk_score=Decimal("98.50"),
        risk_reasons=[
            "Enterprise tier customer",
            "Severe sentiment degradation",
            "Imminent contract renewal"
        ],
        escalation_candidate=True,
    )


# ==============================================================================
# INTEGRATION & CONTRACT TESTS
# ==============================================================================

def test_escalation_handoff_contract_generation(
    escalation_service,
    mock_customer_profile,
    sample_signal_assessment,
    sample_risk_assessment,
):
    """
    Verifies that the service successfully maps all input schemas 
    into a valid, strictly-typed EscalationHandoff Pydantic model.
    """
    workflow_id = "WF-ESC-TEST-001"
    
    # Act
    handoff = escalation_service.handoff(
        workflow_id=workflow_id,
        customer_profile=mock_customer_profile,
        signal_assessment=sample_signal_assessment,
        risk_assessment=sample_risk_assessment,
    )

    # Assert Pydantic Validation Passed
    assert isinstance(handoff, EscalationHandoff)

    # Assert Core Mapping
    assert handoff.ticket_id == f"ESC-{workflow_id}"
    assert handoff.customer_id == 999
    assert handoff.customer_email == "urgent.customer@example.com"
    assert handoff.initial_intent == "HIGH_CHURN_RISK"
    assert handoff.initial_sentiment == "furious"
    
    # Verify Urgency Mapping was applied
    assert handoff.initial_urgency == "urgent" 


def test_escalation_message_formatting(
    escalation_service,
    mock_customer_profile,
    sample_signal_assessment,
    sample_risk_assessment,
):
    """
    Verifies that the multi-line string generated for the human supervisor 
    actually contains all the critical intelligence data.
    """
    handoff = escalation_service.handoff(
        workflow_id="WF-MSG-001",
        customer_profile=mock_customer_profile,
        signal_assessment=sample_signal_assessment,
        risk_assessment=sample_risk_assessment,
    )
    
    msg = handoff.message_english
    
    # Assert critical telemetry is present in the human-readable string
    assert "PROACTIVE ESCALATION" in msg
    assert "HIGH_CHURN_RISK" in msg
    assert "98.50" in msg  # Risk Score
    assert "999" in msg    # Customer ID
    assert "enterprise" in msg
    assert "15000.50" in msg
    
    # Assert list serialization worked correctly (newline joins)
    assert "- Enterprise tier customer" in msg
    assert "- Severe sentiment degradation" in msg


@pytest.mark.parametrize(
    "risk_enum, expected_urgency",
    [
        (RiskLevel.LOW, "low"),
        (RiskLevel.MEDIUM, "medium"),
        (RiskLevel.HIGH, "high"),
        (RiskLevel.CRITICAL, "urgent"),
    ]
)
def test_exhaustive_urgency_mapping(
    escalation_service,
    mock_customer_profile,
    sample_signal_assessment,
    risk_enum,
    expected_urgency,
):
    """
    Parametrized contract test: Proves that every single member of the 
    RiskLevel enum successfully maps to an urgency string without 
    throwing a KeyError.
    """
    custom_risk = RiskAssessment(
        risk_level=risk_enum,
        risk_score=Decimal("50.00"),
        risk_reasons=["Testing mapping"],
        escalation_candidate=True
    )
    
    handoff = escalation_service.handoff(
        workflow_id="WF-MAP-001",
        customer_profile=mock_customer_profile,
        signal_assessment=sample_signal_assessment,
        risk_assessment=custom_risk,
    )
    
    assert handoff.initial_urgency == expected_urgency


def test_missing_sentiment_fallback(
    escalation_service,
    sample_signal_assessment,
    sample_risk_assessment,
):
    """
    Verifies that if the customer profile lacks a sentiment history, 
    the system safely falls back to 'unknown' rather than crashing.
    """
    # FIX: Fully define the mock to prevent false-positives on hidden AttributeErrors
    profile_without_sentiment = MagicMock()
    profile_without_sentiment.customer_id = 1
    profile_without_sentiment.customer_email = "test@test.com"
    profile_without_sentiment.tier = "standard"
    profile_without_sentiment.ltv = Decimal("100")
    
    # Simulate missing sentiment
    profile_without_sentiment.last_sentiment = None
    
    # Act
    handoff = escalation_service.handoff(
        workflow_id="WF-NULL-001",
        customer_profile=profile_without_sentiment,
        signal_assessment=sample_signal_assessment,
        risk_assessment=sample_risk_assessment,
    )
    
    # Assert
    assert handoff.initial_sentiment == "unknown"


def test_ticket_id_generation(
    escalation_service,
    mock_customer_profile,
    sample_signal_assessment,
    sample_risk_assessment,
):
    """
    Verifies the deterministic generation of the escalation ticket ID 
    to ensure downstream Escalation Agent tracking remains intact.
    """
    workflow_id = "WF-E2E-777"
    
    handoff = escalation_service.handoff(
        workflow_id=workflow_id,
        customer_profile=mock_customer_profile,
        signal_assessment=sample_signal_assessment,
        risk_assessment=sample_risk_assessment,
    )
    
    # Assert the deterministic prefix is applied
    assert handoff.ticket_id == "ESC-WF-E2E-777"