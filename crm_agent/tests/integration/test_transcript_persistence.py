# tests/integration/test_transcript_flow.py

import pytest
from unittest.mock import MagicMock
from datetime import datetime, UTC
from decimal import Decimal
from pydantic import ValidationError

from crm_agent.services.transcript.transcript_service import TranscriptService
from crm_agent.repositories.transcript_repository import TranscriptRepository
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
    event_id: str = "evt_123",
    ticket_id: str = "TKT-1",
    customer_id: int = 1,
    status: str = "resolved",
    messages: list = None
) -> CRMResolvedEvent:
    """Helper to generate a minimally viable event for transcript creation."""
    
    default_messages = [
        {"role": "user", "content": "Hello"},
        {"role": "assistant", "content": "Hi"}
    ]
    
    return CRMResolvedEvent(
        event=EventMetadata(
            event_id=event_id,
            event_type="ticket.resolved",
            source_agent="refund_agent",
            schema_version="1.0.0",
            created_at=datetime.now(UTC),
        ),
        ticket=TicketMetadata(ticket_id=ticket_id, channel="web"),
        customer=CustomerMetadata(
            customer_id=customer_id,
            customer_email="test@example.com",
            tier="standard",
            ltv=Decimal("100.00"),
        ),
        resolution=ResolutionMetadata(
            status=status,
            resolution_type="standard_resolution",
            resolved_by="refund_agent",
        ),
        decision=DecisionMetadata(decision_code="RESOLVED", review_required=False),
        risk=RiskMetadata(escalated=False, risk_level="LOW"),
        analytics=AnalyticsMetadata(
            intent="support",
            issue_tags=["support"],
            sentiment_start="neutral",
            sentiment_end="neutral",
        ),
        conversation=ConversationMetadata(
            messages=messages if messages is not None else default_messages,
            agents_involved=["refund_agent"],
            original_message="Help",
        ),
    )


# =========================================================
# Fixtures
# =========================================================
@pytest.fixture
def transcript_env():
    mock_repo = MagicMock(spec=TranscriptRepository)
    service = TranscriptService(transcript_repo=mock_repo)
    return {
        "service": service,
        "repo": mock_repo
    }


# =========================================================
# 1. Validation Logic
# =========================================================
def test_missing_event_id(transcript_env):
    event = build_event(event_id="")
    
    with pytest.raises(ValueError, match="event_id"):
        transcript_env["service"].create_transcript(event)
        
    transcript_env["repo"].get_by_ticket_id.assert_not_called()


def test_missing_ticket_id(transcript_env):
    event = build_event(ticket_id="")
    
    with pytest.raises(ValueError, match="ticket_id"):
        transcript_env["service"].create_transcript(event)
        
    transcript_env["repo"].get_by_ticket_id.assert_not_called()


def test_missing_customer_id(transcript_env):
    
    
    with pytest.raises(ValueError, match="customer_id"):
        event = build_event(customer_id=None)
        transcript_env["service"].create_transcript(event)
        
    transcript_env["repo"].get_by_ticket_id.assert_not_called()


def test_missing_resolution_status(transcript_env):
   
    
    with pytest.raises(ValueError, match="status"):
        event = build_event(status="")
        transcript_env["service"].create_transcript(event)
        
    transcript_env["repo"].get_by_ticket_id.assert_not_called()


def test_empty_conversation_allowed(transcript_env):
    # Systems must handle automated/silent tickets that have no dialogue
    event = build_event(messages=[])
    transcript_env["repo"].get_by_ticket_id.return_value = None
    
    transcript_env["service"].create_transcript(event)
    
    # Must proceed to creation, treating empty convo as a Warning, not an Exception
    transcript_env["repo"].create_transcript.assert_called_once_with(event)


# =========================================================
# 2. Duplicate Suppression & Creation
# =========================================================
def test_successful_transcript_creation(transcript_env):
    event = build_event()
    fake_record = MagicMock()
    
    # Simulate first time seeing this ticket
    transcript_env["repo"].get_by_ticket_id.return_value = None
    transcript_env["repo"].create_transcript.return_value = fake_record

    result = transcript_env["service"].create_transcript(event)

    transcript_env["repo"].get_by_ticket_id.assert_called_once_with("TKT-1")
    transcript_env["repo"].create_transcript.assert_called_once_with(event)
    assert result == fake_record


def test_duplicate_transcript_returns_existing(transcript_env):
    event = build_event()
    existing_record = MagicMock()
    
    # Simulate a network retry where this ticket was already processed
    transcript_env["repo"].get_by_ticket_id.return_value = existing_record

    result = transcript_env["service"].create_transcript(event)

    # Must short-circuit and return the existing record to prevent DB integrity errors
    transcript_env["repo"].create_transcript.assert_not_called()
    assert result == existing_record


def test_repository_failure_propagates(transcript_env):
    event = build_event()
    
    transcript_env["repo"].get_by_ticket_id.return_value = None
    transcript_env["repo"].create_transcript.side_effect = Exception("DB Failure")

    # The service MUST NOT swallow the exception. It must bubble up to the 
    # EventProcessor so the global transaction rolls back.
    with pytest.raises(Exception, match="DB Failure"):
        transcript_env["service"].create_transcript(event)


# =========================================================
# 3. Read Operations (Delegation)
# =========================================================
def test_get_customer_history(transcript_env):
    records = [MagicMock(), MagicMock()]
    transcript_env["repo"].get_customer_history.return_value = records

    result = transcript_env["service"].get_customer_history(customer_id=1, limit=10)

    transcript_env["repo"].get_customer_history.assert_called_once_with(1, 10)
    assert result == records


def test_get_ticket_transcript(transcript_env):
    record = MagicMock()
    transcript_env["repo"].get_by_ticket_id.return_value = record

    result = transcript_env["service"].get_ticket_transcript("TKT-999")

    transcript_env["repo"].get_by_ticket_id.assert_called_once_with("TKT-999")
    assert result == record