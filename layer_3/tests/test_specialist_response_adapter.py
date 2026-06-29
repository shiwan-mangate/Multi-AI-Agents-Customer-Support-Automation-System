import sys
from pathlib import Path

# --- Path Routing Fix ---
current_dir = Path(__file__).parent.resolve()
layer_3_dir = current_dir.parent.resolve()
root_dir = layer_3_dir.parent.resolve()

if str(layer_3_dir) not in sys.path: sys.path.insert(0, str(layer_3_dir))
if str(root_dir) not in sys.path: sys.path.insert(0, str(root_dir))

import pytest
from datetime import datetime, timezone

# Specialist Adapter & Request Schema
from integrations.specialist_response_adapter import SpecialistResponseAdapter
from layer_3.schemas.translation_request import TranslationRequest

# Layer 2 Agent Schemas
from layer_2_faq.schemas.faq_output import FAQAgentOutput
from layer_2_refund.schemas.refund_models import RefundOutput, RefundStatus
from layer_2_account_agent.schemas.final_account_agent_responce import AccountAgentResponse
from layer_2_proactive_agent.schemas.proactive_output import ProactiveOutput
from layer_2_proactive_agent.schemas.outreach_message import OutreachMessage
from layer_2_escalation_agent.schemas.escalation_output import EscalationAgentResponse, EscalationResponse

class TestSpecialistResponseAdapter:

    @pytest.fixture
    def adapter(self):
        return SpecialistResponseAdapter()

    # ==========================================================
    # 1-4. FAQ AGENT TESTS
    # ==========================================================
    def test_faq_resolved(self, adapter):
        output = FAQAgentOutput(
            ticket_id="T1", customer_id=1, status="resolved",
            decision_target="customer", answer="Your refund is approved.",
            completed_at=datetime.now(timezone.utc), citations=[]
        )
        result = adapter.from_faq(output, "hi")
        assert result is not None
        assert result.ticket_id == "T1"
        assert result.source_agent == "faq_agent"
        assert result.english_response == "Your refund is approved."

    def test_faq_clarification_required(self, adapter):
        output = FAQAgentOutput(
            ticket_id="T1", customer_id=1, status="clarification_required",
            decision_target="customer", clarification_question="Which order are you referring to?",
            completed_at=datetime.now(timezone.utc), citations=[]
        )
        result = adapter.from_faq(output, "hi")
        assert result is not None
        assert result.english_response == "Which order are you referring to?"

    def test_faq_escalated(self, adapter):
        output = FAQAgentOutput(
            ticket_id="T1", customer_id=1, status="escalated",
            decision_target="escalation_agent", escalation_reason="Human review required",
            completed_at=datetime.now(timezone.utc), citations=[]
        )
        result = adapter.from_faq(output, "hi")
        assert result is not None
        assert result.english_response == "Human review required"

    def test_faq_returns_none_when_text_missing(self, adapter):
        output = FAQAgentOutput(
            ticket_id="T1", customer_id=1, status="resolved",
            decision_target="customer", answer=None,
            completed_at=datetime.now(timezone.utc), citations=[]
        )
        result = adapter.from_faq(output, "hi")
        assert result is None

    # ==========================================================
    # 5-6. REFUND AGENT TESTS
    # ==========================================================
    def test_refund_output(self, adapter):
        output = RefundOutput(
            ticket_id="T1", workflow_id="WF1", customer_id=1, order_id=100,
            final_status=RefundStatus.COMPLETED, decision_code="APPROVED",
            decision_reason="Policy approved", customer_response="Refund processed successfully.",
            audit_status="SUCCESS"
        )
        result = adapter.from_refund(output, "hi")
        assert result is not None
        assert result.source_agent == "refund_agent"
        assert result.english_response == "Refund processed successfully."

    def test_refund_missing_customer_response(self, adapter):
        output = RefundOutput(
            ticket_id="T1", workflow_id="WF1", customer_id=1, order_id=100,
            final_status=RefundStatus.COMPLETED, decision_code="APPROVED",
            decision_reason="Policy approved", customer_response=None,
            audit_status="SUCCESS"
        )
        result = adapter.from_refund(output, "hi")
        assert result is None

    # ==========================================================
    # 7-8. ACCOUNT AGENT TESTS
    # ==========================================================
    def test_account_output(self, adapter):
        output = AccountAgentResponse(
            ticket_id="T1", customer_id=1, workflow_id="WF1", correlation_id="COR1",
            status="completed", execution_success=True, customer_response="Password reset completed.",
            escalation_required=False, security_escalation=False, audit_logged=True,
            sub_category="x", requested_action="x", decision_reason="x", verification_level="x",
            risk_level="x", provider_name="x", provider_status="x", provider_response={},
            escalation_reason=None, audit_decision="x"
        )
        result = adapter.from_account(output, "hi")
        assert result is not None
        assert result.source_agent == "account_agent"

    def test_account_missing_response(self, adapter):
        output = AccountAgentResponse(
            ticket_id="T1", customer_id=1, workflow_id="WF1", correlation_id="COR1",
            status="completed", execution_success=True, customer_response="", 
            escalation_required=False, security_escalation=False, audit_logged=True,
            sub_category="x", requested_action="x", decision_reason="x", verification_level="x",
            risk_level="x", provider_name="x", provider_status="x", provider_response={},
            escalation_reason=None, audit_decision="x"
        )
        result = adapter.from_account(output, "hi")
        assert result is None

    # ==========================================================
    # 9-11. PROACTIVE AGENT TESTS
    # ==========================================================
    def test_proactive_outreach(self, adapter):
        output = ProactiveOutput(
            workflow_id="WF1", customer_id=1, status="OUTREACH_CREATED",
            outreach_message=OutreachMessage(subject="Hello", body="We miss you.", generated_by="AI")
        )
        result = adapter.from_proactive(output, "hi")
        assert result is not None
        assert result.source_agent == "proactive_agent"
        assert result.english_response == "We miss you."

    def test_proactive_without_message(self, adapter):
        output = ProactiveOutput(workflow_id="WF1", customer_id=1, status="SUPPRESSED", outreach_message=None)
        result = adapter.from_proactive(output, "hi")
        assert result is None

    def test_proactive_empty_body(self, adapter):
        output = ProactiveOutput(
            workflow_id="WF1", customer_id=1, status="OUTREACH_CREATED",
            outreach_message=OutreachMessage(subject="Hello", body="", generated_by="AI")
        )
        result = adapter.from_proactive(output, "hi")
        assert result is None

    # ==========================================================
    # 12-14. ESCALATION AGENT TESTS
    # ==========================================================
    def test_escalation_output(self, adapter):
        resp = EscalationResponse(
            status="ESCALATED",
            error_message="Your case has been escalated."
        )
        output = EscalationAgentResponse(
            status="ESCALATED", ticket_id="T1", customer_id=1, source_agent="refund_agent",
            response=resp
        )
        result = adapter.from_escalation(output, "hi")
        assert result is not None
        assert result.source_agent == "escalation_agent"
        assert "escalated" in result.english_response.lower()

    def test_escalation_missing_response(self, adapter):
        output = EscalationAgentResponse(
            status="ESCALATED", ticket_id="T1", customer_id=1, source_agent="refund_agent",
            response=None
        )
        result = adapter.from_escalation(output, "hi")
        assert result is None

    def test_escalation_missing_customer_message(self, adapter):
        resp = EscalationResponse(status="ESCALATED", error_message=None)
        output = EscalationAgentResponse(
            status="ESCALATED", ticket_id="T1", customer_id=1, source_agent="refund_agent",
            response=resp
        )
        result = adapter.from_escalation(output, "hi")
        assert result is None

    # ==========================================================
    # 15-20. GENERIC ADAPT TESTS
    # ==========================================================
    def test_adapt_faq(self, adapter):
        output = FAQAgentOutput(ticket_id="T1", customer_id=1, status="resolved", answer="Hi", completed_at=datetime.now(timezone.utc), decision_target="customer", citations=[])
        assert adapter.adapt(output, "hi").source_agent == "faq_agent"

    def test_adapt_refund(self, adapter):
        output = RefundOutput(ticket_id="T1", workflow_id="WF1", customer_id=1, order_id=1, final_status=RefundStatus.COMPLETED, decision_code="A", decision_reason="A", customer_response="Hi", audit_status="S")
        assert adapter.adapt(output, "hi").source_agent == "refund_agent"

    def test_adapt_account(self, adapter):
        output = AccountAgentResponse(
            ticket_id="T1", customer_id=1, workflow_id="WF1", correlation_id="C1", status="completed", 
            execution_success=True, customer_response="Hi", escalation_required=False, security_escalation=False, 
            audit_logged=True, sub_category="x", requested_action="x", decision_reason="x", 
            verification_level="x", risk_level="x", provider_name="x", provider_status="x", 
            provider_response={}, escalation_reason=None, audit_decision="x"
        )
        assert adapter.adapt(output, "hi").source_agent == "account_agent"

    def test_adapt_proactive(self, adapter):
        output = ProactiveOutput(workflow_id="WF1", customer_id=1, status="OUTREACH_CREATED", outreach_message=OutreachMessage(subject="S", body="B", generated_by="AI"))
        assert adapter.adapt(output, "hi").source_agent == "proactive_agent"

    def test_adapt_escalation(self, adapter):
        resp = EscalationResponse(status="ESCALATED", error_message="Hi")
        output = EscalationAgentResponse(
            status="ESCALATED", ticket_id="T1", customer_id=1, source_agent="R",
            response=resp
        )
        result = adapter.adapt(output, "hi")
        assert result is not None
        assert result.source_agent == "escalation_agent"

    def test_adapt_unsupported_type(self, adapter):
        assert adapter.adapt({"bad": "data"}, "hi") is None