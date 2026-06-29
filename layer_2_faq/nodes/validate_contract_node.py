from datetime import datetime, UTC
from typing import Dict, Any

from ..schemas.faq_state import FAQState


def validate_contract_node(state: FAQState) -> Dict[str, Any]:
    """
    Deterministic runtime safety gate for the FAQ agent.

    Responsibilities:
    - verify ticket ownership (faq_agent)
    - block inherited escalations
    - validate ticket payload integrity
    - emit structured audit logs
    """

    now = datetime.now(UTC)
    ticket_id = state.get("ticket_id")
    errors: list[str] = []

    
    assigned_agent = state.get("assigned_agent")
    if assigned_agent != "faq_agent":
        errors.append(
            f"Route mismatch: expected 'faq_agent', got '{assigned_agent}'"
        )

    
    if state.get("escalation_required") is True:
        errors.append(
            "Ticket already flagged for escalation by upstream workflow."
        )

    
    ticket = state.get("ticket")
    if not isinstance(ticket, dict) or not ticket.get("message_raw"):
        errors.append(
            "Missing or malformed ticket message content."
        )

    
    contract_valid = len(errors) == 0

    escalation_reason = None
    decision_target = None

    if not contract_valid:
        escalation_reason = errors[0]
        decision_target = "escalation_agent"

    
    log_message = (
        "Contract validation successful."
        if contract_valid
        else f"Contract validation failed: {escalation_reason}"
    )

    return {
        "current_node": "validate_contract_node",
        "updated_at": now,
        "decision_target": decision_target,
        "escalation_required": not contract_valid,
        "escalation_reason": escalation_reason,
        "errors": errors,
        "workflow_logs": [
            {
                "timestamp": now.isoformat(),
                "node": "validate_contract_node",
                "message": log_message,
                "data": {
                    "ticket_id": ticket_id,
                    "contract_valid": contract_valid,
                    "error_count": len(errors),
                    "errors": errors,
                },
            }
        ],
    }