import logging

from layer_2_refund.graphs.refund_state import RefundState

from layer_2_refund.repositories.customer_repository import (
    CustomerRepository
)

from layer_2_refund.schemas.refund_models import (
    PolicyDecision,
    RefundStatus
)

# Import the SessionLocal factory
from layer_2_refund.database.session import SessionLocal

logger = logging.getLogger(__name__)


def customer_node(state: RefundState):

    existing_decision = state.get(
        "policy_decision"
    )

    if existing_decision:

        skip_log = (
            f"Customer Node | "
            f"Status=SKIPPED | "
            f"Existing="
            f"{existing_decision.status.value.upper()}"
        )

        logger.info(skip_log)

        return {
            "current_node": "customer_node",
            "workflow_logs": [
                *state["workflow_logs"],
                skip_log
            ]
        }

    order = state.get("order_data")

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

    if not order:

        decision = PolicyDecision(
            status=RefundStatus.ESCALATED,
            code="ORDER_CONTEXT_MISSING",
            reason=(
                "Customer retrieval failed due "
                "to missing order context."
            ),
            requires_human_review=True
        )

        failure_log = (
            f"Customer Node | "
            f"Status=CRITICAL_FAILURE | "
            f"{ctx} | "
            f"Code={decision.code}"
        )

        logger.error(failure_log)

        return {
            "current_node": "customer_node",
            "policy_decision": decision,
            "error_message": (
                "Customer node executed "
                "without required order context."
            ),
            "workflow_logs": [
                *state["workflow_logs"],
                failure_log
            ]
        }

    customer_id = order.customer_id
    
    # 1. Initialize session as None for the finally block
    session = None
    customer_data = None

    # 2. Safe Database Scope
    try:
        session = SessionLocal()
        
        repo = CustomerRepository(
            session=session
        )

        customer_data = (
            repo.get_customer_by_id(
                customer_id
            )
        )

    except Exception as e:
        
        # If DB fails, escalate to human instead of crashing workflow
        failure_log = (
            f"Customer Node | "
            f"Status=CRITICAL_DB_FAILURE | "
            f"{ctx} | "
            f"Error={str(e)}"
        )
        
        logger.error(failure_log)
        
        decision = PolicyDecision(
            status=RefundStatus.ESCALATED,
            code="DATABASE_ERROR",
            reason=(
                f"Failed to query customer database "
                f"for ID={customer_id}."
            ),
            requires_human_review=True
        )
        
        return {
            "current_node": "customer_node",
            "policy_decision": decision,
            "error_message": "Customer database query failed.",
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
    if customer_data is None:

        decision = PolicyDecision(
            status=RefundStatus.REJECTED,
            code="CUSTOMER_NOT_FOUND",
            reason=(
                "Customer profile associated "
                "with the order could not "
                "be located."
            ),
            requires_human_review=False
        )

        rejection_log = (
            f"Customer Node | "
            f"Status=REJECTED | "
            f"{ctx} | "
            f"Code={decision.code} | "
            f"Customer={customer_id}"
        )

        logger.warning(rejection_log)

        return {
            "current_node": "customer_node",
            "policy_decision": decision,
            "error_message": (
                f"Customer lookup failed "
                f"for ID={customer_id}"
            ),
            "workflow_logs": [
                *state["workflow_logs"],
                rejection_log
            ]
        }

    success_log = (
        f"Customer Node | "
        f"Status=SUCCESS | "
        f"{ctx} | "
        f"Customer={customer_id}"
    )

    logger.info(success_log)

    return {
        "current_node": "customer_node",
        "customer_data": customer_data,
        "workflow_logs": [
            *state["workflow_logs"],
            success_log
        ]
    }