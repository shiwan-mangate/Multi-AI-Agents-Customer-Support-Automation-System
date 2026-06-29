import logging
from layer_2_refund.graphs.refund_state import RefundState
from layer_2_refund.schemas.refund_models import (
    RefundStatus
)

logger = logging.getLogger(__name__)


def route_after_idempotency(
    state: RefundState
) -> str:
    decision = state.get("policy_decision")
    workflow_id = state.get("workflow_id")
    if decision:
        logger.info(
            f"Router | "
            f"Route=IDEMPOTENT_REPLAY | "
            f"Workflow={workflow_id}"
        )
        return "audit_node"
    logger.info(
        f"Router | "
        f"Route=NEW_WORKFLOW | "
        f"Workflow={workflow_id}"
    )
    return "order_node"



def route_after_policy(
    state: RefundState
) -> str:
    decision = state.get("policy_decision")
    workflow_id = state.get("workflow_id")

    # --- DIAGNOSTIC LOG START ---
    logger.warning(
        "ROUTER LOG | route_after_policy | POLICY_STATUS = %s",
        decision.status.value if decision else "NONE"
    )
    # --- DIAGNOSTIC LOG END ---

    if not decision:
        logger.error(
            f"Router | "
            f"Route=FAILSAFE_AUDIT | "
            f"Workflow={workflow_id} | "
            f"Reason=Missing Decision"
        )
        return "audit_node"
    if decision.status == RefundStatus.APPROVED:
        logger.info(
            f"Router | "
            f"Route=EXECUTION | "
            f"Workflow={workflow_id}"
        )
        return "execution_node"
    if decision.status == RefundStatus.ESCALATED:
        logger.warning(
            f"Router | "
            f"Route=ESCALATION | "
            f"Workflow={workflow_id}"
        )
        return "escalation_node"
    if decision.status == RefundStatus.REJECTED:
        logger.info(
            f"Router | "
            f"Route=AUDIT_REJECTED | "
            f"Workflow={workflow_id}"
        )
        return "audit_node"
    logger.error(
        f"Router | "
        f"Route=UNKNOWN_STATE | "
        f"Workflow={workflow_id} | "
        f"Status={decision.status.value}"
    )
    return "audit_node"



def route_after_human_review(
    state: RefundState
) -> str:

    workflow_id = state.get("workflow_id")
    decision = state.get("policy_decision")
    human_decision = state.get("human_decision")

    # --- DIAGNOSTIC LOG START ---
    logger.warning(
        "ROUTER LOG | route_after_human_review | KEYS IN STATE = %s",
        list(state.keys())
    )
    logger.warning(
        "ROUTER LOG | route_after_human_review | HUMAN_DECISION = %s | POLICY_STATUS = %s",
        human_decision,
        decision.status.value if decision else "NONE"
    )
    # --- DIAGNOSTIC LOG END ---

    if not decision:

        logger.error(
            f"Router | "
            f"Route=FAILSAFE_AUDIT | "
            f"Workflow={workflow_id}"
        )

        return "audit_node"

    if decision.status == RefundStatus.ESCALATED:

        logger.info(
            f"Router | "
            f"Route=WAITING_FOR_HUMAN | "
            f"Workflow={workflow_id}"
        )

        return "human_review_node"

    if decision.status == RefundStatus.APPROVED:

        logger.info(
            f"Router | "
            f"Route=EXECUTION_AFTER_HUMAN | "
            f"Workflow={workflow_id}"
        )

        return "execution_node"

    logger.info(
        f"Router | "
        f"Route=AUDIT_AFTER_HUMAN | "
        f"Workflow={workflow_id}"
    )

    return "audit_node"