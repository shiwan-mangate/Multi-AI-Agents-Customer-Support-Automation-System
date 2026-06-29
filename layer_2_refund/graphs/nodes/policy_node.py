from layer_2_refund.graphs.refund_state import (
    RefundState
)

from layer_2_refund.agents.refund_agent.policy_engine import (
    evaluate_refund
)

from layer_2_refund.schemas.refund_models import (
    PolicyDecision,
    RefundStatus
)

import logging
logger = logging.getLogger(__name__)



def policy_node(state: RefundState):

    existing_decision = state.get(
        "policy_decision"
    )

    if existing_decision:

        return {
            "current_node": "policy_node",
            "workflow_logs": [
                *state["workflow_logs"],
                (
                    f"Policy Node | "
                    f"Status=SKIPPED | "
                    f"Existing="
                    f"{existing_decision.status.value.upper()}"
                )
            ]
        }

    order = state.get("order_data")

    customer = state.get("customer_data")

    workflow_id = state.get(
        "workflow_id"
    )

    idempotency_key = state.get(
        "idempotency_key"
    )

    ctx = (
        f"Workflow={workflow_id} | "
        f"Key={idempotency_key}"
    )

    if not order or not customer:

        decision = PolicyDecision(
            status=RefundStatus.ESCALATED,
            code="DATA_INTEGRITY_FAILURE",
            reason=(
                "Policy evaluation failed due to "
                "missing order/customer context."
            ),
            requires_human_review=True
        )

        return {
            "current_node": "policy_node",
            "policy_decision": decision,
            "error_message": (
                "Missing required workflow "
                "context for policy evaluation."
            ),
            "workflow_logs": [
                *state["workflow_logs"],
                (
                    f"Policy Node | "
                    f"Status={decision.status.value.upper()} | "
                    f"Code={decision.code} | "
                    f"{ctx}"
                )
            ]
        }

    decision = evaluate_refund(
        order,
        customer
    )

    logger.warning(
        "POLICY RESULT | status=%s | code=%s | reason=%s",
        decision.status.value,
        decision.code,
        decision.reason
    )

    return {
        "current_node": "policy_node",
        "policy_decision": decision,
        "workflow_logs": [
            *state["workflow_logs"],
            (
                f"Policy Node | "
                f"Status={decision.status.value.upper()} | "
                f"Code={decision.code} | "
                f"{ctx}"
            )
        ]
    }