import pytest
from datetime import datetime, UTC, timedelta
from decimal import Decimal

from crm_agent.services.churn.churn_engine import ChurnEngine
from crm_agent.schemas.crm_event import (
    CRMResolvedEvent, 
    EventMetadata, 
    TicketMetadata, 
    CustomerMetadata,
    ResolutionMetadata,
    RiskMetadata,
    DecisionMetadata,
    AnalyticsMetadata,
    ConversationMetadata
)
# Ensure the model import matches your workspace convention
from crm_agent.db.models.customer_profile_model import CustomerProfile


# =========================================================
# Helper Builders
# =========================================================
def build_profile(
    total_failures: int = 0,
    total_denials: int = 0,
    total_escalations: int = 0,
    negative_ticket_count: int = 0,
    last_sentiment: str = "neutral",
    sentiment_history: list[str] = None,
    last_ticket_at: datetime = None,
    tier: str = "standard",
    ltv: str = "100.00"
) -> CustomerProfile:
    """
    Helper to generate a realistic profile without database insertion.
    Aligned with the updated flat customer_support_profiles table schema.
    """
    return CustomerProfile(
        customer_id=1,  # Fits into database bigint type safely
        customer_email="test@example.com",
        tier=tier,
        ltv=Decimal(ltv),  # Preserves precision for the numeric type
        
        # Explicit counters
        total_tickets=total_failures + total_denials + total_escalations + 1,
        total_faq_tickets=0,
        total_refund_tickets=0,
        total_account_tickets=0,
        total_escalations=total_escalations,
        total_denials=total_denials,
        total_failures=total_failures,
        total_clarifications=0,
        total_duplicate_suppressions=0,
        
        repeat_negative_count=negative_ticket_count,
        repeat_escalation_count=0,
        duplicate_request_count=0,
        negative_ticket_count=negative_ticket_count,
        
        # Flat schema collections matching ARRAY and jsonb data types
        last_sentiment=last_sentiment,
        sentiment_history=sentiment_history or [],
        issue_frequency={},
        agent_interaction_frequency={},
        languages_used=["en"],
        preferred_language="en",
        
        # Base analytics metrics for calculations
        churn_score=Decimal("0.00"),
        churn_level="LOW",
        churn_last_updated=datetime.now(UTC),
        first_seen_at=datetime.now(UTC) - timedelta(days=365),
        last_ticket_at=last_ticket_at or datetime.now(UTC),
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC)
    )


def build_event(
    status: str = "resolved", 
    escalated: bool = False,
    sentiment_end: str = "neutral"
) -> CRMResolvedEvent:
    """Helper to generate a minimal viable CRM event for churn evaluation."""
    return CRMResolvedEvent(
        event=EventMetadata(
            event_id="evt_1", 
            event_type="ticket.resolved",
            source_agent="faq_agent",
            schema_version="1.0",
            created_at=datetime.now(UTC)
        ),
        ticket=TicketMetadata(ticket_id="TKT-1", channel="web"),
        customer=CustomerMetadata(
            customer_id=1, 
            customer_email="test@example.com", 
            tier="standard", 
            ltv=Decimal("100.00")
        ),
        resolution=ResolutionMetadata(
            status=status, 
            resolution_type="test", 
            resolved_by="test_agent"
        ),
        decision=DecisionMetadata(
            decision_code="TEST", 
            review_required=False
        ),
        risk=RiskMetadata(
            escalated=escalated, 
            risk_level="LOW"
        ),
        analytics=AnalyticsMetadata(
            intent="test",
            issue_tags=["test"],
            sentiment_start="neutral",
            sentiment_end=sentiment_end
        ),
        conversation=ConversationMetadata(
            messages=[],
            agents_involved=[],
            original_message="Test query",
            translated_message=None 
        )
    )


# =========================================================
# 1. Scoring Logic Tests
# =========================================================
def test_historical_failures():
    engine = ChurnEngine()
    profile = build_profile(total_failures=3)
    event = build_event()

    assessment = engine.calculate_churn_risk(profile, event)
    
    # 3 failures * 10 weight = 30.00
    assert assessment.churn_score >= Decimal("30.00")


def test_escalation_pattern():
    engine = ChurnEngine()
    profile = build_profile(total_escalations=4)
    event = build_event()

    assessment = engine.calculate_churn_risk(profile, event)
    
    # 4 escalations * 15 + 15 chronic penalty = 75.00
    assert assessment.churn_score >= Decimal("75.00")
    assert assessment.churn_level in ["HIGH", "CRITICAL"]
    assert any("escalation" in reason.lower() for reason in assessment.risk_reasons)


def test_angry_sentiment_current_event():
    engine = ChurnEngine()
    profile = build_profile()
    event = build_event(sentiment_end="angry")

    assessment = engine.calculate_churn_risk(profile, event)
    
    # +25.00 score for current angry sentiment
    assert assessment.churn_score >= Decimal("25.00")


def test_repeated_angry_history():
    engine = ChurnEngine()
    profile = build_profile(
        sentiment_history=["angry", "angry"]
    )
    event = build_event()

    assessment = engine.calculate_churn_risk(profile, event)
    
    # +20.00 score for historical anger
    assert assessment.churn_score >= Decimal("20.00")


def test_inactivity_penalty():
    engine = ChurnEngine()
    stale_date = datetime.now(UTC) - timedelta(days=90)
    profile = build_profile(last_ticket_at=stale_date)
    event = build_event()

    assessment = engine.calculate_churn_risk(profile, event)
    
    # +20.00 score for inactivity > 60 days
    assert assessment.churn_score >= Decimal("20.00")
    assert any("inactivity" in reason.lower() or "lapse" in reason.lower() for reason in assessment.risk_reasons)


# =========================================================
# 2. Business Rules & Multipliers
# =========================================================
def test_vip_multiplier():
    engine = ChurnEngine()
    
    failures = 2
    escalations = 1
    
    standard_profile = build_profile(
        total_failures=failures, 
        total_escalations=escalations, 
        tier="standard", 
        ltv="100.00"
    )
    
    vip_profile = build_profile(
        total_failures=failures, 
        total_escalations=escalations, 
        tier="enterprise", 
        ltv="10000.00"
    )
    
    event = build_event()

    standard_assessment = engine.calculate_churn_risk(standard_profile, event)
    vip_assessment = engine.calculate_churn_risk(vip_profile, event)

    assert vip_assessment.churn_score > standard_assessment.churn_score
    
    # VIP score is standard * 1.30
    expected_vip_score = standard_assessment.churn_score * Decimal("1.30")
    assert vip_assessment.churn_score == expected_vip_score
    
    assert any("vip" in reason.lower() for reason in vip_assessment.risk_reasons)


# =========================================================
# 3. Boundary & Stability Validations
# =========================================================
def test_score_clamp():
    engine = ChurnEngine()
    
    profile = build_profile(
        total_failures=100, 
        total_escalations=100, 
        tier="enterprise", 
        ltv="999999.00"
    )
    event = build_event(sentiment_end="angry")

    assessment = engine.calculate_churn_risk(profile, event)

    # Engine must clamp max score to exactly 100.00
    assert assessment.churn_score == Decimal("100.00")
    assert assessment.churn_level == "CRITICAL"


def test_deterministic_output():
    engine = ChurnEngine()
    profile = build_profile(
        total_failures=2, 
        total_escalations=1,
        sentiment_history=["frustrated", "neutral"],
        tier="premium"
    )
    event = build_event(escalated=True)

    assessment_1 = engine.calculate_churn_risk(profile, event)
    assessment_2 = engine.calculate_churn_risk(profile, event)

    assert assessment_1.churn_score == assessment_2.churn_score
    assert assessment_1.churn_level == assessment_2.churn_level
    assert assessment_1.risk_reasons == assessment_2.risk_reasons