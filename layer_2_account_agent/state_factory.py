import uuid
from datetime import datetime, UTC
from typing import Dict, Any, Optional

from layer_2_account_agent.schemas.account_state import AccountState
from layer_2_account_agent.schemas.domain import WorkflowLog


def parse_datetime(dt_val: Any) -> Optional[datetime]:
    """
    Safely parse datetime values whether they arrive as ISO strings, 
    Unix timestamps, or existing datetime objects.
    """
    if not dt_val:
        return None

   
    if isinstance(dt_val, datetime):
        return dt_val

   
    if isinstance(dt_val, str):
        try:
            return datetime.fromisoformat(dt_val.replace("Z", "+00:00"))
        except (ValueError, TypeError):
            pass 
        
        try:
            return datetime.fromtimestamp(float(dt_val), UTC)
        except (ValueError, TypeError):
            return None

    
    if isinstance(dt_val, (int, float)):
        try:
            return datetime.fromtimestamp(dt_val, UTC)
        except (ValueError, TypeError, OSError):
            return None

    return None


def safe_float(value: Any, default: float = 0.0) -> float:
    """Safely coerce numeric values."""
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def safe_int(value: Any, default: int = 0) -> int:
    """Safely coerce integer values."""
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


class AccountStateFactory:
    """
    Factory for transforming Triage Agent output into a fully initialized
    Account Agent workflow state.
    """

    @staticmethod
    def from_triage_output(triage_payload: Dict[str, Any]) -> AccountState:
        """
        Transform validated triage payload into AccountState.

        Expected source:
            Layer 2 Triage Agent dispatch output.
        """

        # ---------- Contract Validation ----------
        next_agent = triage_payload.get("next_agent")
        if next_agent != "account_agent":
            raise ValueError(
                f"Invalid routing payload: expected next_agent='account_agent', got '{next_agent}'"
            )

        workflow_id = f"acc-wf-{uuid.uuid4().hex[:8]}"
        correlation_id = uuid.uuid4().hex
        now = datetime.now(UTC)

        sla_deadline = parse_datetime(triage_payload.get("sla_deadline")) or now

        state: AccountState = {
            # ---------- Input Contract ----------
            "ticket": triage_payload.get("ticket", {}),
            "entities": triage_payload.get("entities", {}),
            "ticket_id": triage_payload.get("ticket_id", "UNKNOWN"),
            "customer_email": triage_payload.get("customer_email"),
            "customer_id": triage_payload.get("customer_id"),

            # ---------- Supervisor / Triage Context ----------
            "initial_intent": triage_payload.get("initial_intent", "account_issue"),
            "initial_urgency": triage_payload.get("initial_urgency", "medium"),
            "initial_sentiment": triage_payload.get("initial_sentiment", "neutral"),
            "supervisor_confidence": safe_float(
                triage_payload.get("supervisor_confidence"), 0.0
            ),

            "customer_tier": triage_payload.get("customer_tier", "standard"),
            "ltv": safe_float(triage_payload.get("ltv"), 0.0),
            "unresolved_repeat_count": safe_int(
                triage_payload.get("unresolved_repeat_count"), 0
            ),
            "total_tickets": safe_int(triage_payload.get("total_tickets"), 0),
            "total_escalations": safe_int(triage_payload.get("total_escalations"), 0),

            "final_priority": triage_payload.get("final_priority", "medium"),
            "sla_duration_hours": safe_int(
                triage_payload.get("sla_duration_hours"), 24
            ),
            "sla_deadline": sla_deadline,

            # ---------- Classification ----------
            "sub_category": None,
            "clarification_required": False,
            "clarification_question": None,

            # ---------- Identity ----------
            "identity_verified": False,
            "identity_confidence": 0.0,
            "verification_level": None,
            "resolved_customer_id": None,
            "identity_signals": {},

            # ---------- Security ----------
            "risk_assessment": None,
            "escalation_required": False,
            "security_escalation": False,
            "escalation_reason": None,

            # ---------- Context ----------
            "auth_context": {},
            "billing_context": {},
            "subscription_context": {},
            "access_context": {},

            # ---------- Decision ----------
            "decision": None,

            # ---------- Execution ----------
            "action_result": None,
            "provider_response": None,
            "rollback_status": None,
            "idempotency_key": None,

            # ---------- Observability ----------
            "workflow_logs": [],
            "errors": [],
            "retry_count": 0,
            "current_node": "validate_contract_node",
            "created_at": now,
            "workflow_id": workflow_id,
            "correlation_id": correlation_id,
        }

        init_log = WorkflowLog(
            node="state_factory",
            message="Account workflow initialized from triage dispatch payload.",
            data={
                "workflow_id": workflow_id,
                "correlation_id": correlation_id,
                "ticket_id": state["ticket_id"],
                "intent": state["initial_intent"],
                "priority": state["final_priority"],
                "next_agent": next_agent,
            },
        )

        state["workflow_logs"].append(init_log)

        return state