import logging

from layer_2_refund.graphs.refund_state import (
    RefundState
)

from layer_2_refund.schemas.refund_models import (
    RefundStatus
)

logger = logging.getLogger(__name__)


def human_review_node(state: RefundState):

    decision = state.get("policy_decision")

    workflow_id = state.get("workflow_id")

    idempotency_key = state.get(
        "idempotency_key"
    )

    ctx = (
        f"Workflow={workflow_id} | "
        f"Key={idempotency_key}"
    )

    if not decision:

        error_log = (
            f"Human Node | "
            f"Status=ERROR | "
            f"{ctx} | "
            f"Reason=Missing Decision"
        )

        logger.error(error_log)

        return {
            "current_node": "human_review_node",
            "error_message": (
                "Human review triggered "
                "without policy decision."
            ),
            "workflow_logs": [
                *state["workflow_logs"],
                error_log
            ]
        }

    if decision.status != RefundStatus.ESCALATED:

        skip_log = (
            f"Human Node | "
            f"Status=SKIPPED | "
            f"{ctx} | "
            f"CurrentStatus="
            f"{decision.status.value.upper()}"
        )

        logger.info(skip_log)

        return {
            "current_node": "human_review_node",
            "workflow_logs": [
                *state["workflow_logs"],
                skip_log
            ]
        }

    human_choice = (
        state.get("human_decision")
    )

    if not human_choice:

        waiting_log = (
            f"Human Node | "
            f"Status=AWAITING_INPUT | "
            f"{ctx} | "
            f"Reason={decision.code}"
        )

        logger.info(waiting_log)

        # --- STEP 1 INJECTION START ---
        logger.warning(
            "PAUSE STATE KEYS = %s",
            list(state.keys())
        )

        logger.warning(
            "PAUSE STATE = %s",
            state
        )
        # --- STEP 1 INJECTION END ---

        return {
            "current_node": "human_review_node",
            "review_status": "PENDING",
            "workflow_logs": [
                *state["workflow_logs"],
                waiting_log
            ]
        }

    human_choice = (
        human_choice
        .strip()
        .upper()
    )

    valid_choices = {
        "APPROVE",
        "REJECT"
    }

    if human_choice not in valid_choices:

        invalid_log = (
            f"Human Node | "
            f"Status=INVALID_INPUT | "
            f"{ctx} | "
            f"Input={human_choice}"
        )

        logger.warning(invalid_log)

        return {
            "current_node": "human_review_node",
            "error_message": (
                "Invalid human decision."
            ),
            "workflow_logs": [
                *state["workflow_logs"],
                invalid_log
            ]
        }

    if human_choice == "APPROVE":

        final_status = (
            RefundStatus.APPROVED
        )

        final_code = (
            "HUMAN_APPROVED"
        )

    else:

        final_status = (
            RefundStatus.REJECTED
        )

        final_code = (
            "HUMAN_REJECTED"
        )

    updated_decision = (
        decision.model_copy(
            update={
                "status": final_status,
                "code": final_code,
                "reason": (
                    f"Human Review Result: "
                    f"{human_choice}"
                ),

                "refund_amount": (
                    decision.refund_amount
                    or decision.metadata.get("order_amount")
                ),

                "requires_human_review": False,

                "metadata": {
                    **decision.metadata,
                    "human_review_decision":
                        human_choice
                }
            }
        )
    )

    resolved_log = (
        f"Human Node | "
        f"Status=RESOLVED | "
        f"{ctx} | "
        f"Action={final_code}"
    )

    logger.info(resolved_log)

    return {
        "current_node": "human_review_node",
        "policy_decision": updated_decision,
        "human_decision": human_choice,
        "review_status": "COMPLETED",
        "workflow_logs": [
            *state["workflow_logs"],
            resolved_log
        ]
    }