import logging

from layer_2_refund.graphs.refund_state import (
    RefundState
)

from layer_2_refund.repositories.order_repository import (
    OrderRepository
)

from layer_2_refund.schemas.refund_models import (
    PolicyDecision,
    RefundStatus
)

# Import the SessionLocal factory
from layer_2_refund.database.session import SessionLocal

logger = logging.getLogger(__name__)


def order_node(state: RefundState):

    existing_decision = state.get(
        "policy_decision"
    )

    if existing_decision:

        skip_log = (
            f"Order Node | "
            f"Status=SKIPPED | "
            f"Existing="
            f"{existing_decision.status.value.upper()}"
        )

        logger.info(skip_log)

        return {
            "current_node": "order_node",
            "workflow_logs": [
                *state["workflow_logs"],
                skip_log
            ]
        }

    request = state.get("request")

    workflow_id = state.get(
        "workflow_id"
    )

    id_key = state.get(
        "idempotency_key"
    )

    ctx = (
        f"Workflow={workflow_id} | "
        f"Key={id_key}"
    )

    # 1. State Guard
    if not request:

        decision = PolicyDecision(
            status=RefundStatus.ESCALATED,
            code="REQUEST_CONTEXT_MISSING",
            reason=(
                "Order retrieval failed due "
                "to missing request context."
            ),
            requires_human_review=True
        )

        failure_log = (
            f"Order Node | "
            f"Status=CRITICAL_FAILURE | "
            f"{ctx} | "
            f"Code={decision.code}"
        )

        logger.error(failure_log)

        return {
            "current_node": "order_node",
            "policy_decision": decision,
            "error_message": (
                "Order node executed without "
                "required request context."
            ),
            "workflow_logs": [
                *state["workflow_logs"],
                failure_log
            ]
        }

    # 2. Safe Database Scope
    session = None
    order_data = None

    try:
        # Open connection
        session = SessionLocal()
        
        order_repo = OrderRepository(
            session=session
        )

        # Query the database
        order_data = (
            order_repo.get_order_by_id(
                request.order_id
            )
        )

    except Exception as e:
        
        failure_log = (
            f"Order Node | "
            f"Status=CRITICAL_DB_FAILURE | "
            f"{ctx} | "
            f"Error={str(e)}"
        )
        
        logger.error(failure_log)
        
        decision = PolicyDecision(
            status=RefundStatus.ESCALATED,
            code="DATABASE_ERROR",
            reason=(
                f"Failed to query order database "
                f"for OrderID={request.order_id}."
            ),
            requires_human_review=True
        )
        
        return {
            "current_node": "order_node",
            "policy_decision": decision,
            "error_message": "Order database query failed.",
            "workflow_logs": [
                *state["workflow_logs"],
                failure_log
            ]
        }

    finally:
        # 3. Guaranteed Cleanup
        if session:
            session.close()

    # 4. Process the safely extracted data
    if order_data is None:

        decision = PolicyDecision(
            status=RefundStatus.REJECTED,
            code="ORDER_NOT_FOUND",
            reason=(
                "The provided order ID "
                "does not exist."
            ),
            requires_human_review=False
        )

        rejection_log = (
            f"Order Node | "
            f"Status=REJECTED | "
            f"{ctx} | "
            f"Code={decision.code} | "
            f"Order={request.order_id}"
        )

        logger.warning(rejection_log)

        return {
            "current_node": "order_node",
            "policy_decision": decision,
            "error_message": (
                f"Order lookup failed "
                f"for OrderID={request.order_id}"
            ),
            "workflow_logs": [
                *state["workflow_logs"],
                rejection_log
            ]
        }

    success_log = (
        f"Order Node | "
        f"Status=SUCCESS | "
        f"{ctx} | "
        f"Order={request.order_id}"
    )

    logger.info(success_log)

    return {
        "current_node": "order_node",
        "order_data": order_data,
        "workflow_logs": [
            *state["workflow_logs"],
            success_log
        ]
    }