import pytest
from decimal import Decimal
from unittest.mock import MagicMock

from layer_2_proactive_agent.services.risk_engine import RiskEngine
from layer_2_proactive_agent.schemas.enums import RiskLevel
from layer_2_proactive_agent.schemas.risk_assessment import RiskAssessment

@pytest.fixture
def engine():
    return RiskEngine()

def create_mock_inputs(severity, churn_level, tier, ticket_count):
    signal_assessment = MagicMock()
    # FIX: Directly assign the Enum instance, do not try to set .value
    signal_assessment.severity = severity 

    profile = MagicMock()
    profile.customer_id = 123
    profile.churn_intelligence.churn_level = churn_level
    profile.tier = tier
    profile.negative_ticket_count = ticket_count

    return signal_assessment, profile

@pytest.mark.parametrize(
    "severity, churn, tier, tickets, expected_score, expected_level, expected_escalation",
    [
        (RiskLevel.CRITICAL, "CRITICAL", "enterprise", 5, Decimal("100.00"), RiskLevel.CRITICAL, True),
        (RiskLevel.HIGH, "MEDIUM", "standard", 0, Decimal("90.00"), RiskLevel.CRITICAL, True),
        (RiskLevel.MEDIUM, "LOW", "enterprise", 0, Decimal("60.00"), RiskLevel.HIGH, True),
        (RiskLevel.MEDIUM, "MEDIUM", "standard", 0, Decimal("60.00"), RiskLevel.HIGH, False),
        (RiskLevel.LOW, "MEDIUM", "standard", 0, Decimal("40.00"), RiskLevel.MEDIUM, False),
        (RiskLevel.LOW, "LOW", "standard", 0, Decimal("20.00"), RiskLevel.LOW, False),
    ]
)
def test_risk_engine_score_matrix(
    engine, severity, churn, tier, tickets, expected_score, expected_level, expected_escalation
):
    """
    Exhaustively tests the additive scoring logic and level boundaries.
    """
    signal, profile = create_mock_inputs(severity, churn, tier, tickets)
    result = engine.assess(signal, profile)
    
    assert result.risk_score == expected_score
    assert result.risk_level == expected_level
    assert result.escalation_candidate == expected_escalation

def test_risk_engine_history_score_capping(engine):
    """
    Proves that the negative ticket history score is correctly
    calculated as (count * 2) but strictly capped at a maximum of 20.
    """
    # 15 tickets * 2 = 30 (should cap at 20)
    # LOW[10] + LOW[10] + standard[0] + history[20] = 40 (MEDIUM)
    signal, profile = create_mock_inputs(RiskLevel.LOW, "LOW", "standard", 15)
    result = engine.assess(signal, profile)
    
    assert result.risk_score == Decimal("40.00")
    assert result.risk_level == RiskLevel.MEDIUM

def test_risk_engine_reasons_generation(engine):
    """
    Verifies that the engine correctly appends highly specific
    human-readable strings to the risk_reasons list.
    """
    signal, profile = create_mock_inputs(RiskLevel.HIGH, "CRITICAL", "premium", 5)
    result = engine.assess(signal, profile)
    
    assert any("Signal severity=HIGH" in r for r in result.risk_reasons)
    assert any("Customer churn level=CRITICAL" in r for r in result.risk_reasons)
    assert any("Customer tier=premium" in r for r in result.risk_reasons)
    assert any("Negative ticket history=5" in r for r in result.risk_reasons)

def test_risk_engine_high_boundary(engine):
    """
    Verify score=78 remains HIGH and does not become CRITICAL.
    """
    # severity(MEDIUM=30) + churn(MEDIUM=30) + tier(premium=10) + tickets(4*2=8) = 78
    signal, profile = create_mock_inputs(RiskLevel.MEDIUM, "MEDIUM", "premium", 4)
    result = engine.assess(signal, profile)
    
    assert result.risk_score == Decimal("78.00")
    assert result.risk_level == RiskLevel.HIGH
    assert result.escalation_candidate is False

def test_risk_engine_enterprise_high_risk_escalation(engine):
    """
    Enterprise customers at HIGH risk should become escalation candidates.
    """
    # severity(MEDIUM=30) + churn(LOW=10) + tier(enterprise=20) + tickets(0) = 60
    signal, profile = create_mock_inputs(RiskLevel.MEDIUM, "LOW", "enterprise", 0)
    result = engine.assess(signal, profile)
    
    assert result.risk_score == Decimal("60.00")
    assert result.risk_level == RiskLevel.HIGH
    assert result.escalation_candidate is True
    assert any("Enterprise customer with high risk" in r for r in result.risk_reasons)

def test_risk_engine_critical_always_escalates(engine):
    """
    CRITICAL risk must always escalate, regardless of tier.
    """
    # severity(CRITICAL=90) + churn(CRITICAL=90) -> capped at 100
    signal, profile = create_mock_inputs(RiskLevel.CRITICAL, "CRITICAL", "standard", 0)
    result = engine.assess(signal, profile)
    
    assert result.risk_level == RiskLevel.CRITICAL
    assert result.escalation_candidate is True
    assert any("Critical risk threshold exceeded" in r for r in result.risk_reasons)

def test_risk_engine_returns_complete_model(engine):
    """
    Ensures the engine returns a fully compliant RiskAssessment object.
    """
    signal, profile = create_mock_inputs(RiskLevel.LOW, "LOW", "standard", 0)
    result = engine.assess(signal, profile)
    
    assert isinstance(result, RiskAssessment)
    assert hasattr(result, "risk_level")
    assert hasattr(result, "risk_score")
    assert hasattr(result, "risk_reasons")
    assert hasattr(result, "escalation_candidate")