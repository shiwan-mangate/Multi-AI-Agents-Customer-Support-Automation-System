import uuid
import logging
from datetime import datetime, UTC
from typing import Dict, Any

from layer_2_escalation_agent.schemas.escalation_state import EscalationState

logger = logging.getLogger(__name__)

VALID_ESCALATION_SOURCES = {
    "supervisor",
    "triage_agent",
    "refund_agent",
    "faq_agent",
    "account_agent",
    "proactive_agent",
    "system",
}


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


class EscalationStateFactory:
    """
    Factory for normalizing upstream escalation payloads into a
    fully initialized EscalationState for LangGraph execution.
    """

    @staticmethod
    def from_payload(payload: Dict[str, Any]) -> EscalationState:
        """
        Build normalized EscalationState from arbitrary upstream payload.
        """

        source_agent = payload.get("source_agent", "system")

        if source_agent not in VALID_ESCALATION_SOURCES:
            raise ValueError(
                f"Invalid escalation source_agent: '{source_agent}'"
            )

        now = datetime.now(UTC)

        workflow_id = f"esc-wf-{uuid.uuid4().hex[:8]}"
        correlation_id = uuid.uuid4().hex

        ticket = payload.get("ticket", {})
        
        # Refactored: ticket_id must remain a string to align with character varying
        raw_ticket_id = payload.get("ticket_id") or ticket.get("ticket_id") or ""
        ticket_id = str(raw_ticket_id).strip()

        # customer_id maps perfectly to system-wide BigInt
        customer_id = safe_int(payload.get("customer_id") or ticket.get("customer_id"), 0)

        # Refactored: Ensure entities defaults to a list to match EscalationState
        entities = payload.get("entities")
        if not isinstance(entities, list):
            if isinstance(entities, dict) and entities:
                entities = [entities]
            else:
                entities = []

        state: EscalationState = {
            "ticket": ticket,
            "ticket_id": ticket_id,
            "customer_id": customer_id,
            "customer_email": payload.get("customer_email") or ticket.get("customer_email") or "",
            "source_agent": source_agent,
            "initial_intent": payload.get("initial_intent", "faq"),
            "initial_sentiment": payload.get("initial_sentiment", "neutral"),
            "initial_urgency": payload.get("initial_urgency", "medium"),
            "supervisor_confidence": safe_float(
                payload.get("supervisor_confidence"),
                0.0
            ),
            "entities": entities,
            "workflow_logs": payload.get("workflow_logs") or [],

            "trigger_assessment": None,
            "customer_context": None,
            "conversation_context": None,
            "risk_assessment": None,
            
            # Refactored: Default to absolute boolean flags to prevent NoneType evaluation panics
            "review_required": None,
            "review_completed": None,
            "human_decision": None,
            "audit_status": None,

            "holding_message": None,
            "holding_sent": False,

            "human_brief": None,
            "routing_decision": None,

            "case_id": f"esc-{uuid.uuid4().hex[:12]}",
            "notification_jobs": [],

            "response": None,

            "current_node": "state_factory",
            "errors": [],
            "metrics": {
                "workflow_id": workflow_id,
                "correlation_id": correlation_id,
                "started_at": now.isoformat(),
                "source_agent": source_agent,
                "ticket_id": ticket_id,
            },
        }

        state["workflow_logs"].append(
            {
                "timestamp": now.isoformat(),
                "node": "state_factory",
                "message": "Escalation workflow initialized.",
                "data": {
                    "workflow_id": workflow_id,
                    "correlation_id": correlation_id,
                    "ticket_id": ticket_id,
                    "customer_id": customer_id,
                    "source_agent": source_agent,
                },
            }
        )

        logger.info(
            "Escalation workflow initialized | "
            f"Ticket={ticket_id} | "
            f"Customer={customer_id} | "
            f"Source={source_agent}"
        )

        return state