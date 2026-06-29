import logging
from datetime import datetime, UTC

from layer_2_escalation_agent.schemas.escalation_state import EscalationState

logger = logging.getLogger(__name__)


def validate_contract_node(state: EscalationState) -> EscalationState:
    """
    Validate escalation workflow input contract.

    Responsibilities:
    - fail-fast contract validation (aborts execution on schema failure)
    - workflow observability logging

    No DB access.
    No business logic.
    """
    logger.info("Executing validate_contract_node")

    state["current_node"] = "validate_contract_node"

    errors = []

    ticket = state.get("ticket", {})

    # Refactored: Standardized validation guards against string character variations
    raw_ticket_id = state.get("ticket_id")
    ticket_id = str(raw_ticket_id).strip() if raw_ticket_id is not None else ""
    if not ticket_id:
        errors.append("Missing required field: ticket_id")

    if not state.get("customer_id"):
        errors.append("Missing required field: customer_id")

    if not state.get("source_agent"):
        errors.append("Missing required field: source_agent")

    if not ticket:
        errors.append("Missing required ticket payload")
    else:
        message_raw = ticket.get("message_raw")
        message_english = ticket.get("message_english")

        if not str(message_raw or "").strip() and not str(message_english or "").strip():
            errors.append(
                "Ticket payload missing customer message content"
            )

    if errors:
        state["errors"].extend(errors)

        log_entry = {
            "node": "validate_contract_node",
            "timestamp": datetime.now(UTC).isoformat(),
            "message": "Contract validation failed",
            "data": {
                "errors": errors
            },
        }

        state["workflow_logs"].append(log_entry)

        logger.error(
            "Contract validation failed | ticket_id=%s | errors=%s",
            ticket_id or "unknown",
            errors,
        )

        # Refactored: Implemented true fail-fast behavior by raising a structural 
        # error to keep corrupted payloads out of the multi-agent graph pipelines
        raise ValueError(f"Contract validation aborted: {', '.join(errors)}")

    log_entry = {
        "node": "validate_contract_node",
        "timestamp": datetime.now(UTC).isoformat(),
        "message": "Escalation input contract validated successfully.",
        "data": {
            "ticket_id": ticket_id,
            "customer_id": state["customer_id"],
            "source_agent": state["source_agent"],
        },
    }

    state["workflow_logs"].append(log_entry)

    logger.info(
        "Contract validation successful | ticket_id=%s",
        ticket_id,
    )

    return state