import pytest
from unittest.mock import MagicMock
from collections import namedtuple

# Fix 1: Corrected import paths based on your architecture
from crm_agent.services.processing.event_processor import EventProcessor
from crm_agent.services.processing.event_router import EventRouter
from crm_agent.adapters.refund_adapter import RefundAdapter

MockChurnAssessment = namedtuple("MockChurnAssessment", ["churn_level", "churn_score", "risk_reasons"])

# =========================================================
# 1. Orchestration Fixture
# =========================================================
@pytest.fixture
def crm_flow():
    """Builds the entire CRM stack with a mix of real logic and mocked databases."""
    session = MagicMock()
    idempotency = MagicMock()
    event_repo = MagicMock()
    transcript_repo = MagicMock()
    profile_repo = MagicMock()
    alert_repo = MagicMock()
    churn_engine = MagicMock()

    # Fix 4: Set up default mock profile so downstream logic (Churn) doesn't break
    fake_profile = MagicMock()
    fake_profile.customer_id = 10592
    profile_repo.get_profile.return_value = fake_profile

    # Fix 5: Set up default safe return for alert checks
    alert_repo.get_open_alert.return_value = None

    # Real Router
    router = EventRouter()

    # Real Processor (Orchestrator)
    processor = EventProcessor(
        session=session,
        router=router,
        idempotency_service=idempotency,
        event_repo=event_repo,
        transcript_repo=transcript_repo,
        profile_repo=profile_repo,
        alert_repo=alert_repo,
        churn_engine=churn_engine,
    )

    # Real Adapter
    adapter = RefundAdapter()

    return {
        "session": session,
        "idempotency": idempotency,
        "event_repo": event_repo,
        "transcript_repo": transcript_repo,
        "profile_repo": profile_repo,
        "alert_repo": alert_repo,
        "churn_engine": churn_engine,
        "processor": processor,
        "adapter": adapter,
    }

# =========================================================
# Helper: Standard Global Context
# =========================================================
def get_global_context():
    return {
        "event_id": "evt_999",
        "customer_id": 10592,
        "customer_email": "vip@example.com",
        "tier": "premium",   # Fix 2: Matched BaseAdapter keys
        "ltv": 1500.00,      # Fix 3: Matched BaseAdapter keys
        "channel": "web",
        "sentiment_start": "neutral",
        "sentiment_end": "happy",
        "original_message": "I never received my order. I want a refund.",
        "conversation_history": [
            {"role": "user", "content": "I never received my order. I want a refund."},
            {"role": "assistant", "content": "Refund issued successfully."}
        ]
    }

def get_refund_output():
    return {
        "ticket_id": "T-1001",
        "assigned_agent": "refund_agent",
        "status": "resolved",
        "resolution": {
            "resolution_type": "refund_completed",
            "message": "Refund issued successfully",
            "refund_amount": 49.99,
            "currency": "USD"
        },
        "decision": {
            "decision_code": "APPROVED",
            "decision_reason": "Policy matched"
        }
    }

# =========================================================
# 2. End-to-End Flow Tests
# =========================================================

def test_adapter_to_processor_contract(crm_flow):
    """Verifies adapter output strictly matches the processor's required inputs."""
    crm_event = crm_flow["adapter"].to_crm_event(get_refund_output(), get_global_context())
    
    assert crm_event.customer.customer_id == 10592
    assert crm_event.customer.tier == "premium"
    assert crm_event.customer.ltv == 1500.00
    assert crm_event.event.source_agent == "refund_agent"
    assert crm_event.resolution.resolution_type == "refund_completed"

def test_refund_flow_success(crm_flow):
    """The Happy Path: Validates standard refund output ripples through the whole system."""
    crm_event = crm_flow["adapter"].to_crm_event(get_refund_output(), get_global_context())
    crm_flow["idempotency"].is_duplicate_event.return_value = False
    
    # Process
    crm_flow["processor"].process_event(crm_event)
    
    # Fix 7: Tightened assertions to verify exact object routing
    crm_flow["transcript_repo"].create_transcript.assert_called_once_with(crm_event)
    crm_flow["profile_repo"].upsert_profile_from_event.assert_called_once_with(crm_event)
    
    # Depending on your exact implementation, idempotency and event_repo might take the ID or the Event
    crm_flow["idempotency"].mark_success.assert_called_once()
    crm_flow["event_repo"].mark_done.assert_called_once()
    crm_flow["session"].commit.assert_called_once()

def test_duplicate_refund_flow(crm_flow):
    """Validates that duplicate events short-circuit and protect the database."""
    crm_event = crm_flow["adapter"].to_crm_event(get_refund_output(), get_global_context())
    crm_flow["idempotency"].is_duplicate_event.return_value = True
    
    crm_flow["processor"].process_event(crm_event)
    
    # Verify short-circuit
    crm_flow["transcript_repo"].create_transcript.assert_not_called()
    crm_flow["profile_repo"].upsert_profile_from_event.assert_not_called()

def test_failed_refund_triggers_churn(crm_flow):
    """Validates that a bad customer experience correctly routes to the Churn Engine."""
    context = get_global_context()
    context["tier"] = "standard"
    
    crm_event = crm_flow["adapter"].to_crm_event(get_refund_output(), context)
    
    crm_event.analytics.sentiment_end = "angry"
    crm_event.resolution.status = "failed"
    
    crm_flow["idempotency"].is_duplicate_event.return_value = False
    
    # FIX: Drop the simulated risk to MEDIUM so it updates the profile but skips the alert
    assessment = MockChurnAssessment(churn_level="MEDIUM", churn_score=50, risk_reasons=["frustrated"])
    crm_flow["churn_engine"].calculate_churn_risk.return_value = assessment
    
    crm_flow["processor"].process_event(crm_event)
    
    # Verify the churn path was taken
    crm_flow["churn_engine"].calculate_churn_risk.assert_called_once()
    crm_flow["profile_repo"].update_churn_state.assert_called_once()
    
    # NOW this will correctly assert not called, because MEDIUM churn skips the alert
    crm_flow["alert_repo"].create_alert.assert_not_called()


def test_critical_churn_creates_alert(crm_flow):
    """Validates that extremely high churn risk triggers immediate escalation alerts."""
    crm_event = crm_flow["adapter"].to_crm_event(get_refund_output(), get_global_context())
    crm_event.analytics.sentiment_end = "angry"
    crm_event.resolution.status = "failed"
    
    crm_flow["idempotency"].is_duplicate_event.return_value = False
    
    # Mock the churn assessment to be Critical
    assessment = MockChurnAssessment(churn_level="CRITICAL", churn_score=95, risk_reasons=["vip rage"])
    crm_flow["churn_engine"].calculate_churn_risk.return_value = assessment
    
    crm_flow["processor"].process_event(crm_event)
    
    crm_flow["alert_repo"].create_alert.assert_called_once()
    crm_flow["profile_repo"].update_churn_state.assert_called_once()

def test_repository_failure_rolls_back(crm_flow):
    """Validates that a crash during processing safely rolls back the database transaction."""
    crm_event = crm_flow["adapter"].to_crm_event(get_refund_output(), get_global_context())
    crm_flow["idempotency"].is_duplicate_event.return_value = False
    
    # Simulate a database failure deep in the pipeline
    crm_flow["transcript_repo"].create_transcript.side_effect = Exception("Database timeout")
    
    # Fix 6: Removed pytest.raises; testing the processor's internal exception handling directly.
    crm_flow["processor"].process_event(crm_event)
        
    # Verify the safety net triggered
    crm_flow["session"].rollback.assert_called_once()
    crm_flow["event_repo"].mark_failed.assert_called_once()