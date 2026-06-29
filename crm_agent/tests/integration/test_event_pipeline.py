# tests/integration/test_event_pipeline.py

import pytest
from unittest.mock import MagicMock
from datetime import datetime, UTC
from decimal import Decimal

from crm_agent.services.processing.event_processor import EventProcessor
from crm_agent.services.processing.event_router import EventRouter
from crm_agent.services.ingestion.idempotency_service import IdempotencyService
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
    ConversationMetadata,
)

# =========================================================
# Helpers
# =========================================================
def build_event(
    source_agent: str = "refund_agent",
    resolution_type: str = "refund_completed",
    status: str = "resolved",
    sentiment_end: str = "neutral",
    tier: str = "standard"
) -> CRMResolvedEvent:
    return CRMResolvedEvent(
        event=EventMetadata(
            event_id="evt_pipe_123",
            event_type="ticket.resolved",
            source_agent=source_agent,
            schema_version="1.0.0",
            created_at=datetime.now(UTC),
        ),
        ticket=TicketMetadata(ticket_id="TKT-100", channel="web"),
        customer=CustomerMetadata(
            customer_id=1,
            customer_email="test@example.com",
            tier=tier,
            ltv=Decimal("100.00"),
        ),
        resolution=ResolutionMetadata(
            status=status,
            resolution_type=resolution_type,
            resolved_by=source_agent,
        ),
        decision=DecisionMetadata(decision_code="TEST_EXEC", review_required=False),
        risk=RiskMetadata(escalated=(status == "escalated"), risk_level="LOW"),
        analytics=AnalyticsMetadata(
            intent="support",
            issue_tags=["support"],
            sentiment_start="neutral",
            sentiment_end=sentiment_end,
        ),
        conversation=ConversationMetadata(
            messages=[{"role": "user", "content": "help"}],
            agents_involved=[source_agent],
            original_message="help",
        ),
    )


# =========================================================
# Fixtures
# =========================================================
@pytest.fixture
def pipeline_env():
    session = MagicMock()

    event_repo = MagicMock()
    transcript_repo = MagicMock()
    profile_repo = MagicMock()
    alert_repo = MagicMock()

    idem_service = MagicMock(spec=IdempotencyService)
    churn_engine = MagicMock(spec=ChurnEngine)

    router = EventRouter()

    processor = EventProcessor(
        session=session,
        router=router,
        idempotency_service=idem_service,
        churn_engine=churn_engine,
        event_repo=event_repo,
        transcript_repo=transcript_repo,
        profile_repo=profile_repo,
        alert_repo=alert_repo,
    )

    return {
        "processor": processor,
        "session": session,
        "event_repo": event_repo,
        "transcript_repo": transcript_repo,
        "profile_repo": profile_repo,
        "alert_repo": alert_repo,
        "idem": idem_service,
        "churn_engine": churn_engine,
    }


# =========================================================
# 1. Happy Path & Duplicates
# =========================================================
def test_successful_processing(pipeline_env):
    env = pipeline_env

    event = build_event(
        source_agent="refund_agent",
        resolution_type="refund_completed",
        status="resolved",
    )

    env["idem"].is_duplicate_event.return_value = False

    env["processor"].process_event(event)

    env["transcript_repo"].create_transcript.assert_called_once_with(event)
    env["profile_repo"].upsert_profile_from_event.assert_called_once_with(event)
    env["idem"].mark_success.assert_called_once_with(event)
    env["event_repo"].mark_done.assert_called_once_with(event.event.event_id)
    env["session"].commit.assert_called_once()


def test_duplicate_event_skipped(pipeline_env):
    env = pipeline_env
    event = build_event()
    
    env["idem"].is_duplicate_event.return_value = True

    env["processor"].process_event(event)

    env["transcript_repo"].create_transcript.assert_not_called()
    env["profile_repo"].upsert_profile_from_event.assert_not_called()
    env["event_repo"].mark_done.assert_called_once_with(event.event.event_id)
    env["session"].commit.assert_called_once()


# =========================================================
# 2. Router Validation & Dead Letters
# =========================================================
def test_dead_letter_unknown_agent(pipeline_env):
    env = pipeline_env
    event = build_event(source_agent="alien_agent")

    env["idem"].is_duplicate_event.return_value = False

    env["processor"].process_event(event)

    env["event_repo"].mark_dead.assert_called_once()
    
    # Safe verification of kwargs
    kwargs = env["event_repo"].mark_dead.call_args.kwargs
    assert kwargs["event_id"] == event.event.event_id

    env["idem"].mark_dead.assert_called_once_with(event)
    env["session"].rollback.assert_called_once()
    env["session"].commit.assert_called_once()


def test_invalid_faq_resolution_dead_letter(pipeline_env):
    env = pipeline_env
    event = build_event(source_agent="faq_agent", resolution_type="invalid_type")
    env["idem"].is_duplicate_event.return_value = False

    env["processor"].process_event(event)

    env["event_repo"].mark_dead.assert_called_once()
    env["session"].rollback.assert_called_once()


def test_invalid_refund_resolution_dead_letter(pipeline_env):
    env = pipeline_env
    event = build_event(source_agent="refund_agent", resolution_type="fake_refund")
    env["idem"].is_duplicate_event.return_value = False

    env["processor"].process_event(event)

    env["event_repo"].mark_dead.assert_called_once()
    env["session"].rollback.assert_called_once()


# =========================================================
# 3. Analytics & Alert Routing
# =========================================================
def test_churn_analysis_path(pipeline_env):
    env = pipeline_env

    event = build_event(
        status="failed",
        sentiment_end="angry",
    )

    env["idem"].is_duplicate_event.return_value = False

    fake_profile = MagicMock()
    fake_profile.customer_id = 1
    env["profile_repo"].get_profile.return_value = fake_profile

    fake_assessment = MagicMock()
    fake_assessment.churn_score = Decimal("85.00")
    fake_assessment.churn_level = "HIGH"
    env["churn_engine"].calculate_churn_risk.return_value = fake_assessment

    env["processor"].process_event(event)

    env["profile_repo"].get_profile.assert_called_once_with(event.customer.customer_id)
    env["churn_engine"].calculate_churn_risk.assert_called_once()
    env["profile_repo"].update_churn_state.assert_called_once()


def test_alert_creation_path(pipeline_env):
    env = pipeline_env

    event = build_event(
        status="failed",
        sentiment_end="angry",
        tier="premium",
    )

    env["idem"].is_duplicate_event.return_value = False

    fake_profile = MagicMock()
    fake_profile.customer_id = 1
    env["profile_repo"].get_profile.return_value = fake_profile

    fake_assessment = MagicMock()
    fake_assessment.churn_score = Decimal("95.00")
    fake_assessment.churn_level = "CRITICAL"
    fake_assessment.risk_reasons = ["Angry customer"]
    env["churn_engine"].calculate_churn_risk.return_value = fake_assessment

    env["alert_repo"].get_open_alert.return_value = None

    env["processor"].process_event(event)

    env["alert_repo"].create_alert.assert_called_once()


def test_alert_suppression(pipeline_env):
    env = pipeline_env

    event = build_event(
        status="failed",
        sentiment_end="angry",
        tier="premium",
    )

    env["idem"].is_duplicate_event.return_value = False

    fake_profile = MagicMock()
    fake_profile.customer_id = 1
    env["profile_repo"].get_profile.return_value = fake_profile

    fake_assessment = MagicMock()
    fake_assessment.churn_score = Decimal("95.00")
    fake_assessment.churn_level = "CRITICAL"
    fake_assessment.risk_reasons = ["Angry customer"]
    env["churn_engine"].calculate_churn_risk.return_value = fake_assessment

    # Simulate an open alert already exists
    env["alert_repo"].get_open_alert.return_value = MagicMock()

    env["processor"].process_event(event)

    env["alert_repo"].create_alert.assert_not_called()


# =========================================================
# 4. Critical Failures & Transactions
# =========================================================
def test_missing_profile_marks_failed(pipeline_env):
    env = pipeline_env
    event = build_event(status="failed", sentiment_end="angry")
    env["idem"].is_duplicate_event.return_value = False

    # Return None to simulate missing profile during Churn analysis
    env["profile_repo"].get_profile.return_value = None

    env["processor"].process_event(event)

    env["session"].rollback.assert_called_once()
    env["event_repo"].mark_failed.assert_called_once()


def test_repository_failure_marks_failed(pipeline_env):
    env = pipeline_env
    event = build_event()
    env["idem"].is_duplicate_event.return_value = False

    env["transcript_repo"].create_transcript.side_effect = Exception("DB Error")

    env["processor"].process_event(event)

    env["session"].rollback.assert_called_once()
    env["event_repo"].mark_failed.assert_called_once()


def test_queue_update_failure_reraises(pipeline_env):
    env = pipeline_env
    event = build_event()
    env["idem"].is_duplicate_event.return_value = False
    
    # Dual failure path
    env["transcript_repo"].create_transcript.side_effect = Exception("DB Error")
    env["event_repo"].mark_failed.side_effect = Exception("Queue Update Error")

    with pytest.raises(Exception, match="Queue Update Error"):
        env["processor"].process_event(event)

    # Asserts the transaction rolls back both the initial failure AND the queue failure
    assert env["session"].rollback.call_count == 2