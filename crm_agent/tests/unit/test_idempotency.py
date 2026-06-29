# tests/unit/test_idempotency.py

import pytest
from unittest.mock import MagicMock
from datetime import datetime, UTC
from decimal import Decimal

from crm_agent.services.ingestion.idempotency_service import IdempotencyService
from crm_agent.repositories.processed_event_repository import ProcessedEventRepository
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

# =========================================================
# Helper Builder
# =========================================================
def build_event(event_id: str = "evt_123") -> CRMResolvedEvent:
    """Helper to generate a minimal viable CRM event with a specific ID."""
    return CRMResolvedEvent(
        event=EventMetadata(
            event_id=event_id, 
            event_type="ticket.resolved",
            source_agent="refund_agent",
            schema_version="1.0.0",
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
            status="resolved", 
            resolution_type="test", 
            resolved_by="refund_agent"
        ),
        decision=DecisionMetadata(decision_code="TEST", review_required=False),
        risk=RiskMetadata(escalated=False, risk_level="LOW"),
        analytics=AnalyticsMetadata(
            intent="refund",
            issue_tags=["refund"],
            sentiment_start="neutral",
            sentiment_end="neutral"
        ),
        conversation=ConversationMetadata(
            messages=[],
            agents_involved=["refund_agent"],
            original_message="Test",
            translated_message=None
        )
    )

# =========================================================
# Fixtures
# =========================================================
@pytest.fixture
def idempotency_service():
    """Injects a MagicMock repository into the service."""
    mock_repo = MagicMock(spec=ProcessedEventRepository)
    return IdempotencyService(processed_repo=mock_repo)

# =========================================================
# 1. Duplicate Detection
# =========================================================
def test_new_event_not_duplicate(idempotency_service):
    event = build_event(event_id="evt_new_001")
    
    # Simulate DB finding no record of this event
    idempotency_service.processed_repo.is_processed.return_value = False

    result = idempotency_service.is_duplicate_event(event)

    # Must return False, safe to process
    assert result is False
    idempotency_service.processed_repo.is_processed.assert_called_once_with("evt_new_001")


def test_duplicate_event_detected(idempotency_service):
    event = build_event(event_id="evt_dupe_999")
    
    # Simulate DB finding an existing record 
    idempotency_service.processed_repo.is_processed.return_value = True

    result = idempotency_service.is_duplicate_event(event)

    # Must return True, skip processing to prevent double-processing
    assert result is True
    idempotency_service.processed_repo.is_processed.assert_called_once_with("evt_dupe_999")


def test_deterministic_behavior(idempotency_service):
    event = build_event(event_id="evt_det_000")
    idempotency_service.processed_repo.is_processed.return_value = False

    result1 = idempotency_service.is_duplicate_event(event)
    result2 = idempotency_service.is_duplicate_event(event)

    assert result1 is False
    assert result2 is False
    assert idempotency_service.processed_repo.is_processed.call_count == 2

# =========================================================
# 2. State Mutators
# =========================================================
def test_mark_success(idempotency_service):
    event = build_event(event_id="evt_success_123")
    fake_record = MagicMock()
    idempotency_service.processed_repo.mark_processed.return_value = fake_record

    result = idempotency_service.mark_success(event)

    # Verify the repository was explicitly handed the event_id, not the ticket_id
    idempotency_service.processed_repo.mark_processed.assert_called_once_with("evt_success_123")
    # Verify the service passes the database record back to the caller
    assert result == fake_record


def test_mark_dead(idempotency_service):
    event = build_event(event_id="evt_dead_456")
    fake_record = MagicMock()
    idempotency_service.processed_repo.mark_dead.return_value = fake_record

    result = idempotency_service.mark_dead(event)

    # Verify correct delegation for dead-lettering
    idempotency_service.processed_repo.mark_dead.assert_called_once_with("evt_dead_456")
    # Verify the service passes the database record back to the caller
    assert result == fake_record

# =========================================================
# 3. Error Handling & Stability
# =========================================================
def test_is_processed_failure_bubbles_up(idempotency_service):
    event = build_event(event_id="evt_error_789")
    
    # Simulate a PostgreSQL connection timeout or pool exhaustion
    idempotency_service.processed_repo.is_processed.side_effect = Exception("Database unavailable")

    # The service MUST NOT swallow this error. It must crash and let the EventProcessor rollback.
    with pytest.raises(Exception, match="Database unavailable"):
        idempotency_service.is_duplicate_event(event)


def test_mark_success_failure_bubbles_up(idempotency_service):
    event = build_event(event_id="evt_err_succ")
    
    idempotency_service.processed_repo.mark_processed.side_effect = Exception("DB failure")

    with pytest.raises(Exception, match="DB failure"):
        idempotency_service.mark_success(event)


def test_mark_dead_failure_bubbles_up(idempotency_service):
    event = build_event(event_id="evt_err_dead")
    
    idempotency_service.processed_repo.mark_dead.side_effect = Exception("DB failure")

    with pytest.raises(Exception, match="DB failure"):
        idempotency_service.mark_dead(event)