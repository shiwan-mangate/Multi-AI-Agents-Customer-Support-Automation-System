import logging
from typing import Dict, Any

from layer_2_account_agent.schemas.account_state import AccountState
from layer_2_account_agent.schemas.domain import WorkflowLog

logger = logging.getLogger(__name__)


def clarification_check(state: AccountState) -> Dict[str, Any]:
    """
    Node 3: Clarification routing gate.

    Decides whether workflow should continue
    or pause pending customer clarification.
    """

    ticket_id = state.get("ticket_id")
    clarification_required = state.get("clarification_required", False)
    clarification_question = state.get("clarification_question")

    workflow_logs = list(state.get("workflow_logs", []))

    logger.info(
        "Executing clarification_check node ticket_id=%s",
        ticket_id
    )

    if not clarification_required:
        workflow_logs.append(
            WorkflowLog(
                node="clarification_check_node",
                message="Clarification not required. Workflow continues.",
                data={"ticket_id": ticket_id}
            )
        )

        return {
            "workflow_logs": workflow_logs,
            "current_node": "clarification_check_node"
        }

    workflow_logs.append(
        WorkflowLog(
            node="clarification_check_node",
            message="Workflow paused pending customer clarification.",
            data={
                "ticket_id": ticket_id,
                "clarification_question": clarification_question
            }
        )
    )

    return {
        "escalation_required": True,
        "escalation_reason": "Customer clarification required.",
        "workflow_logs": workflow_logs,
        "current_node": "clarification_check_node"
    }