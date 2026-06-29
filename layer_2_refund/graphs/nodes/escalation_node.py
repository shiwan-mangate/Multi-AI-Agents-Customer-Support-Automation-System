import logging

from layer_2_refund.graphs.refund_state import RefundState

from layer_2_refund.schemas.refund_models import (
    PolicyDecision,
    RefundStatus
)

logger = logging.getLogger(__name__)


def escalation_node(state: RefundState):

    decision = state.get("policy_decision")

    request = state.get("request")

    workflow_id = state.get("workflow_id")

    idempotency_key = state.get(
        "idempotency_key"
    )

    ctx = (
        f"Workflow={workflow_id} | "
        f"Key={idempotency_key} | "
        f"Ticket={request.ticket_id if request else 'N/A'}"
    )

    if not decision:

        fallback_decision = PolicyDecision(
            status=RefundStatus.ESCALATED,
            code="ESCALATION_CONTEXT_MISSING",
            reason=(
                "Escalation workflow triggered "
                "without a valid policy decision."
            ),
            requires_human_review=True
        )

        failure_log = (
            f"Escalation Node | "
            f"Status=CRITICAL_FAILURE | "
            f"{ctx} | "
            f"Code={fallback_decision.code}"
        )

        logger.error(failure_log)

        return {
            "current_node": "escalation_node",
            "policy_decision": fallback_decision,
            "review_status": "PENDING",
            "error_message": (
                "Escalation node missing "
                "required policy context."
            ),
            "workflow_logs": [
                *state["workflow_logs"],
                failure_log
            ]
        }

    if decision.status != RefundStatus.ESCALATED:

        skip_log = (
            f"Escalation Node | "
            f"Status=SKIPPED | "
            f"{ctx} | "
            f"CurrentStatus="
            f"{decision.status.value.upper()}"
        )

        logger.info(skip_log)

        return {
            "current_node": "escalation_node",
            "workflow_logs": [
                *state["workflow_logs"],
                skip_log
            ]
        }

    review_queue = "Support_Lead_Queue"

    escalation_log = (
        f"Escalation Node | "
        f"Status=ALERT_TRIGGERED | "
        f"{ctx} | "
        f"Reason={decision.code} | "
        f"TargetQueue={review_queue}"
    )

    logger.warning(escalation_log)

    updated_decision = decision.model_copy(
        update={
            "metadata": {
                **decision.metadata,
                "review_queue": review_queue,
                "escalated_by_node": "policy_node"
            }
        }
    )

    return {
        "current_node": "escalation_node",
        "policy_decision": updated_decision,
        "review_status": "PENDING",
        "workflow_logs": [
            *state["workflow_logs"],
            escalation_log
        ]
    }