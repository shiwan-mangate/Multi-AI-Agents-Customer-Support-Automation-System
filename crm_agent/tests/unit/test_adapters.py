# tests/unit/test_adapters.py

from decimal import Decimal
import pytest

from crm_agent.adapters.faq_adapter import FAQAdapter
from crm_agent.adapters.refund_adapter import RefundAdapter
from crm_agent.adapters.account_adapter import AccountAdapter
from crm_agent.adapters.escalation_adapter import EscalationAdapter
from crm_agent.schemas.crm_event import CRMResolvedEvent

from crm_agent.tests.fixtures.common import GLOBAL_CONTEXT
from crm_agent.tests.fixtures.faq_payloads import (
    FAQ_SUCCESS_OUTPUT,
    FAQ_CLARIFICATION_OUTPUT,
    FAQ_KNOWLEDGE_GAP_OUTPUT
)
from crm_agent.tests.fixtures.refund_payloads import (
    REFUND_AUTO_APPROVE_OUTPUT,
    REFUND_HUMAN_REVIEW_OUTPUT,
    REFUND_REJECTED_OUTPUT,
    REFUND_IDEMPOTENT_OUTPUT
)
from crm_agent.tests.fixtures.account_payloads import (
    ACCOUNT_PASSWORD_RESET_OUTPUT,
    ACCOUNT_ESCALATION_OUTPUT,
    ACCOUNT_DENIED_OUTPUT
)
from crm_agent.tests.fixtures.escalation_payloads import (
    ESCALATION_SUCCESS_OUTPUT,
    ESCALATION_DUPLICATE_OUTPUT,
    ESCALATION_REVIEW_OUTPUT,
    ESCALATION_FAILED_OUTPUT
)


# =========================================================
# 1. FAQ Adapter Tests
# =========================================================
def test_faq_returns_crm_event():
    """Verify strict contract adherence."""
    adapter = FAQAdapter()
    event = adapter.to_crm_event(FAQ_SUCCESS_OUTPUT, GLOBAL_CONTEXT)
    
    assert isinstance(event, CRMResolvedEvent)


def test_faq_has_no_financial_data():
    adapter = FAQAdapter()
    event = adapter.to_crm_event(FAQ_SUCCESS_OUTPUT, GLOBAL_CONTEXT)
    
    assert event.financial is None


def test_faq_adapter_success():
    adapter = FAQAdapter()
    event = adapter.to_crm_event(FAQ_SUCCESS_OUTPUT, GLOBAL_CONTEXT)

    assert event.event.source_agent == "faq_agent"
    assert event.resolution.status == "resolved"
    assert event.resolution.resolution_type == "faq_answer"
    assert event.decision.decision_code == "FAQ_CONFIDENT"
    assert event.risk.escalated is False
    assert event.risk.risk_level == "LOW"
    
    # Inherits from GLOBAL_CONTEXT, not execution_metadata
    assert event.analytics.intent == "Return Policy"


def test_faq_adapter_clarification():
    adapter = FAQAdapter()
    event = adapter.to_crm_event(FAQ_CLARIFICATION_OUTPUT, GLOBAL_CONTEXT)

    assert event.resolution.status == "clarification_required"
    assert event.resolution.resolution_type == "clarification_requested"
    assert event.decision.decision_code == "CLARIFICATION_REQUIRED"
    # FAQ clarifications do not trigger elevated risk
    assert event.risk.risk_level == "MEDIUM"


def test_faq_adapter_knowledge_gap():
    adapter = FAQAdapter()
    event = adapter.to_crm_event(FAQ_KNOWLEDGE_GAP_OUTPUT, GLOBAL_CONTEXT)

    # Raw status is "handoff", maps to "escalated"
    assert event.resolution.status == "escalated"
    assert event.decision.decision_code == "KNOWLEDGE_GAP"
    assert event.risk.escalated is True
    assert event.risk.risk_level == "HIGH"


# =========================================================
# 2. Refund Adapter Tests
# =========================================================
def test_refund_adapter_auto_approve():
    adapter = RefundAdapter()
    event = adapter.to_crm_event(REFUND_AUTO_APPROVE_OUTPUT, GLOBAL_CONTEXT)

    assert event.event.source_agent == "refund_agent"
    assert event.resolution.status == "resolved"
    
    assert event.financial is not None
    # Use Decimal for financial precision matching
    assert event.financial.refund_amount == Decimal("120.0")
    assert event.financial.currency == "USD"
    assert event.financial.transaction_id == "TXN-A9D44211"
    
    assert event.decision.decision_code == "REFUND_EXECUTED"
    assert event.risk.human_review_required is False
    assert event.risk.risk_level == "LOW"
    assert "refund" in event.analytics.issue_tags


def test_refund_adapter_human_review():
    adapter = RefundAdapter()
    event = adapter.to_crm_event(REFUND_HUMAN_REVIEW_OUTPUT, GLOBAL_CONTEXT)

    assert event.resolution.status == "resolved"
    assert event.decision.review_required is True
    assert event.risk.human_review_required is True
    assert event.risk.risk_level == "MEDIUM"


def test_refund_adapter_rejected():
    adapter = RefundAdapter()
    event = adapter.to_crm_event(REFUND_REJECTED_OUTPUT, GLOBAL_CONTEXT)

    # Adapter maps "closed" to "denied" CRM status
    assert event.resolution.status == "denied"
    assert event.resolution.resolution_type == "refund_rejected"
    assert event.decision.decision_code == "OUTSIDE_WINDOW"
    assert event.risk.risk_level == "LOW" 


def test_refund_adapter_idempotent():
    adapter = RefundAdapter()
    event = adapter.to_crm_event(REFUND_IDEMPOTENT_OUTPUT, GLOBAL_CONTEXT)

    assert event.resolution.status == "resolved"
    assert event.decision.decision_code == "IDEMPOTENT_REPLAY"


# =========================================================
# 3. Account Adapter Tests
# =========================================================
def test_account_adapter_password_reset():
    adapter = AccountAdapter()
    event = adapter.to_crm_event(ACCOUNT_PASSWORD_RESET_OUTPUT, GLOBAL_CONTEXT)

    assert event.event.source_agent == "account_agent"
    assert event.resolution.status == "resolved"
    assert event.decision.verification_level == "PASSED"
    assert event.decision.decision_code == "PASSWORD_RESET"
    
    assert event.financial is None
    assert event.risk.risk_level == "LOW"
    
    assert "account" in event.analytics.issue_tags
    assert "password_reset" in event.analytics.issue_tags


def test_account_adapter_escalation():
    adapter = AccountAdapter()
    event = adapter.to_crm_event(ACCOUNT_ESCALATION_OUTPUT, GLOBAL_CONTEXT)

    assert event.resolution.status == "escalated"
    assert event.decision.verification_level == "FAILED"
    assert event.decision.decision_code == "SECURITY_ESCALATION"
    
    assert event.risk.escalated is True
    assert event.risk.risk_level == "CRITICAL"


def test_account_adapter_denied():
    adapter = AccountAdapter()
    event = adapter.to_crm_event(ACCOUNT_DENIED_OUTPUT, GLOBAL_CONTEXT)

    assert event.resolution.status == "denied"
    assert event.decision.decision_code == "DENIED_BY_POLICY"
    assert event.decision.verification_level == "FAILED"
    assert event.risk.risk_level == "LOW"


# =========================================================
# 4. Escalation Adapter Tests
# =========================================================
def test_escalation_adapter_success():
    adapter = EscalationAdapter()
    event = adapter.to_crm_event(ESCALATION_SUCCESS_OUTPUT, GLOBAL_CONTEXT)

    assert event.resolution.status == "escalated"
    assert event.resolution.resolution_type == "escalation_created"
    assert event.decision.decision_code == "ESCALATION_CREATED"
    
    assert event.financial is None
    assert event.risk.escalated is True
    assert event.risk.risk_level == "HIGH"
    
    assert "escalation" in event.analytics.issue_tags
    assert "retention_team" in event.analytics.issue_tags


def test_escalation_adapter_duplicate():
    adapter = EscalationAdapter()
    event = adapter.to_crm_event(ESCALATION_DUPLICATE_OUTPUT, GLOBAL_CONTEXT)

    assert event.resolution.status == "duplicate_suppressed"
    assert event.resolution.resolution_type == "duplicate_escalation"
    assert event.decision.decision_code == "DUPLICATE_SUPPRESSED"
    
    # Risk remains HIGH because the customer still has an active escalation
    assert event.risk.escalated is True
    assert event.risk.risk_level == "HIGH"


def test_escalation_adapter_human_review():
    adapter = EscalationAdapter()
    event = adapter.to_crm_event(ESCALATION_REVIEW_OUTPUT, GLOBAL_CONTEXT)

    assert event.resolution.status == "human_review_required"
    assert event.decision.decision_code == "HUMAN_REVIEW_REQUIRED"
    
    assert event.risk.human_review_required is True
    assert event.risk.risk_level == "CRITICAL"


def test_escalation_adapter_failed():
    adapter = EscalationAdapter()
    event = adapter.to_crm_event(ESCALATION_FAILED_OUTPUT, GLOBAL_CONTEXT)

    assert event.resolution.status == "failed"
    assert event.decision.decision_code == "ESCALATION_FAILED"
    assert event.risk.escalated is True
    assert event.risk.risk_level == "HIGH"