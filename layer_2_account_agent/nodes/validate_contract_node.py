
import logging
from datetime import datetime, timezone
from typing import Dict, Any
from layer_2_account_agent.schemas.account_state import AccountState
from layer_2_account_agent.schemas.domain import WorkflowLog
logger = logging.getLogger(__name__)


def validate_contract(state: AccountState) -> Dict[str, Any]:
    """
    Node 1: Account agent entry gatekeeper.

    Validates whether the incoming triage payload is safe
    for account workflow processing.
    """

    ticket_id = state.get("ticket_id")

    logger.info(
        "Executing validate_contract node ticket_id=%s",
        ticket_id
    )

    errors = list(state.get("errors", []))
    logs = list(state.get("workflow_logs", []))

    ticket = state.get("ticket")
    customer_email = state.get("customer_email")
    initial_intent = state.get("initial_intent")



    if not ticket:
        errors.append("Ticket context is missing")

    if not ticket_id:
        errors.append("Ticket ID is missing")

    if not customer_email or customer_email == "UNKNOWN":
        errors.append("Customer email is missing")



    escalation_required = len(errors) > 0

    if escalation_required:
        escalation_reason = " | ".join(errors)

        log_message = (
            f"Contract validation failed: {escalation_reason}"
        )

    else:
        escalation_reason = None

        log_message = (
            "Contract validation successful."
        )

    logs.append(
        WorkflowLog(
            node="validate_contract_node",
            message=log_message,
            timestamp=datetime.now(timezone.utc),
            data={
                "errors_found": len(errors),
                "ticket_id": ticket_id
            }
        )
    )

    return {
        "errors": errors,
        "escalation_required": escalation_required,
        "escalation_reason": escalation_reason,
        "workflow_logs": logs,
        "current_node": "validate_contract_node"
    }

