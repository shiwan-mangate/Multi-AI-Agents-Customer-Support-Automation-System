# tests/integration/test_customer_updates.py

import pytest
from unittest.mock import MagicMock
from datetime import datetime, UTC
from decimal import Decimal
from pydantic import ValidationError


from crm_agent.services.customer.profile_service import ProfileService
from crm_agent.repositories.customer_profile_repository import CustomerProfileRepository
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
    customer_id: int = 1,
    source_agent: str = "refund_agent",
    status: str = "resolved",
    sentiment_end: str = "neutral",
) -> CRMResolvedEvent:
    """Generates a valid event, allowing overrides for specific test targets."""
    return CRMResolvedEvent(
        event=EventMetadata(
            event_id="evt_123",
            event_type="ticket.resolved",
            source_agent=source_agent,
            schema_version="1.0.0",
            created_at=datetime.now(UTC),
        ),
        ticket=TicketMetadata(ticket_id="TKT-1", channel="web"),
        customer=CustomerMetadata(
            customer_id=customer_id,
            customer_email="test@example.com",
            tier="standard",
            ltv=Decimal("100.00"),
        ),
        resolution=ResolutionMetadata(
            status=status,
            resolution_type="standard_resolution",
            resolved_by=source_agent,
        ),
        decision=DecisionMetadata(decision_code="RESOLVED", review_required=False),
        risk=RiskMetadata(escalated=(status == "escalated"), risk_level="LOW"),
        analytics=AnalyticsMetadata(
            intent="support",
            issue_tags=["support"],
            sentiment_start="neutral",
            sentiment_end=sentiment_end,
        ),
        conversation=ConversationMetadata(
            messages=[],
            agents_involved=[source_agent],
            original_message="Help",
        ),
    )


# =========================================================
# Fixtures
# =========================================================
@pytest.fixture
def profile_env():
    mock_repo = MagicMock(spec=CustomerProfileRepository)
    service = ProfileService(profile_repo=mock_repo)
    return {
        "service": service,
        "repo": mock_repo
    }


# =========================================================
# 1. Validation Logic
# =========================================================
def test_missing_customer_id(profile_env):
    # The crash happens DURING event creation, so it goes inside the block.
    # We expect Pydantic to catch this, hence ValidationError.
    with pytest.raises(ValidationError):
        event = build_event(customer_id=None)
        profile_env["service"].update_customer_profile(event)

    profile_env["repo"].upsert_profile_from_event.assert_not_called()

def test_missing_source_agent(profile_env):
    event = build_event(source_agent="")

    with pytest.raises(ValueError, match="source_agent"):
        profile_env["service"].update_customer_profile(event)

    profile_env["repo"].upsert_profile_from_event.assert_not_called()


def test_missing_resolution_status(profile_env):
    with pytest.raises(ValidationError):
        event = build_event(status=None)
        profile_env["service"].update_customer_profile(event)

    profile_env["repo"].upsert_profile_from_event.assert_not_called()

# =========================================================
# 2. Orchestration & Delegation
# =========================================================
def test_successful_profile_update(profile_env):
    event = build_event()

    profile_env["service"].update_customer_profile(event)

    # Verifies the orchestrator successfully delegates to the native SQL repo layer
    profile_env["repo"].upsert_profile_from_event.assert_called_once_with(event)


def test_repository_called_once(profile_env):
    event = build_event()

    profile_env["service"].update_customer_profile(event)

    # Explicitly protects against accidental duplicate updates in the service layer
    assert profile_env["repo"].upsert_profile_from_event.call_count == 1


def test_repository_failure_propagates(profile_env):
    event = build_event()
    
    # Simulate a database deadlock or connection drop
    profile_env["repo"].upsert_profile_from_event.side_effect = Exception("Database lock timeout")

    # The service MUST NOT swallow the exception. It must bubble up to the EventProcessor 
    # so the global transaction rolls back.
    with pytest.raises(Exception, match="Database lock timeout"):
        profile_env["service"].update_customer_profile(event)



def test_escalation_event_delegation(profile_env):
    event = build_event(status="escalated")

    profile_env["service"].update_customer_profile(event)

    # Verify the service passes the unmodified, correct event to the repository
    profile_env["repo"].upsert_profile_from_event.assert_called_once()
    called_event = profile_env["repo"].upsert_profile_from_event.call_args.args[0]
    
    assert called_event.resolution.status == "escalated"
    assert called_event.risk.escalated is True


def test_angry_sentiment_delegation(profile_env):
    event = build_event(sentiment_end="angry")

    profile_env["service"].update_customer_profile(event)

    # Verify the service passes the unmodified, correct event to the repository
    profile_env["repo"].upsert_profile_from_event.assert_called_once()
    called_event = profile_env["repo"].upsert_profile_from_event.call_args.args[0]
    
    assert called_event.analytics.sentiment_end == "angry"