import logging
from typing import Dict, Any

from layer_2_account_agent.services.subclassifier import SubclassifierService
from layer_2_account_agent.schemas.account_state import AccountState
from layer_2_account_agent.schemas.domain import WorkflowLog

logger = logging.getLogger(__name__)


def subclassify_issue(
    state: AccountState,
    subclassifier_service: SubclassifierService
) -> Dict[str, Any]:
    """
    Node 2: Subclassify account issue.
    """

    ticket_id = state.get("ticket_id")

    logger.info(
        "Executing subclassify_issue node ticket_id=%s",
        ticket_id
    )

    logs = list(state.get("workflow_logs", []))

    message = state.get("ticket", {}).get("message_raw", "")

    try:
        result = subclassifier_service.classify_issue(message)
        logger.warning(
        "SUBCLASSIFICATION RESULT | ticket=%s | sub_category=%s | clarification_required=%s | question=%s",
        ticket_id,
        result.sub_category,
        result.clarification_required,
        result.clarification_question
    )

        logs.append(
            WorkflowLog(
                node="subclassify_issue_node",
                message=(
                    f"Subclassified issue as "
                    f"{result.sub_category.value if result.sub_category else 'ambiguous'}"
                ),
                data={
                    "ticket_id": ticket_id
                }
            )
        )

        return {
            "sub_category": result.sub_category,
            "clarification_required": result.clarification_required,
            "clarification_question": result.clarification_question,
            "workflow_logs": logs,
            "current_node": "subclassify_issue_node"
        }

    except Exception:
        logger.exception(
            "Subclassification failed ticket_id=%s",
            ticket_id
        )

        logs.append(
            WorkflowLog(
                node="subclassify_issue_node",
                message="Subclassification failed. Clarification fallback triggered.",
                data={
                    "ticket_id": ticket_id
                }
            )
        )

        return {
            "clarification_required": True,
            "clarification_question": (
                "I want to route your account issue correctly. "
                "Is this a login issue, billing issue, "
                "subscription request, or security concern?"
            ),
            "workflow_logs": logs,
            "current_node": "subclassify_issue_node"
        }