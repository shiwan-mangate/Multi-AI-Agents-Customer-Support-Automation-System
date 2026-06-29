from layer_2_account_agent.schemas.account_state import AccountState
from layer_2_account_agent.schemas.domain import (
    ActionType,
    ActionSubCategory,
    WorkflowLog
)

import logging
from datetime import datetime, UTC
from typing import Dict, Any

logger = logging.getLogger(__name__)


def action_resolution_node(
    state: AccountState
) -> Dict[str, Any]:
    """
    Resolve exact executable action from classified intent.
    """

    ticket_id = state.get("ticket_id")
    ticket = state.get("ticket", {})
    sub_category = state.get("sub_category")
    logs = list(state.get("workflow_logs", []))

    message = ticket.get("message_raw", "").lower()

    logger.info(
        "Executing action_resolution_node ticket_id=%s",
        ticket_id
    )

    requested_action = ActionType.SECURITY_ESCALATION

    if sub_category == ActionSubCategory.LOGIN_ISSUE:

        if "locked" in message or "unlock" in message:
            requested_action = ActionType.ACCOUNT_UNLOCK
        else:
            requested_action = ActionType.PASSWORD_RESET

    elif sub_category == ActionSubCategory.BILLING_QUERY:

        if (
            "invoice" in message
            or "receipt" in message
            or "bill pdf" in message
        ):
            requested_action = ActionType.INVOICE_RETRIEVAL
        else:
            requested_action = ActionType.BILLING_EXPLANATION

    elif sub_category == ActionSubCategory.ACCESS_RESTORATION:
        requested_action = ActionType.ACCESS_SYNC

    elif sub_category == ActionSubCategory.SECURITY_ISSUE:
        requested_action = ActionType.SECURITY_ESCALATION

    logs.append(
        WorkflowLog(
            node="action_resolution_node",
            message=(
                f"Resolved requested action "
                f"{requested_action.value}"
            ),
            timestamp=datetime.now(UTC),
            data={
                "ticket_id": ticket_id,
                "sub_category": (
                    sub_category.value
                    if sub_category else None
                )
            }
        )
    )

    return {
        "requested_action": requested_action,
        "workflow_logs": logs,
        "current_node": "action_resolution_node"
    }