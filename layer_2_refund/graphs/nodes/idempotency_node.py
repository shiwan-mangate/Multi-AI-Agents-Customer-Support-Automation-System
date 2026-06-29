import logging

from layer_2_refund.graphs.refund_state import (
    RefundState
)

from layer_2_refund.repositories.refund_repository import (
    RefundRepository
)

# Import the SessionLocal factory
from layer_2_refund.database.session import SessionLocal

logger = logging.getLogger(__name__)


def idempotency_node(state: RefundState):

    idempotency_key = state.get(
        "idempotency_key"
    )

    workflow_id = state.get(
        "workflow_id"
    )

    ctx = (
        f"Workflow={workflow_id} | "
        f"Key={idempotency_key}"
    )

    # 1. State Guard
    if not idempotency_key:

        failure_log = (
            f"Idempotency Node | "
            f"Status=CRITICAL_FAILURE | "
            f"{ctx} | "
            f"Reason=Missing Idempotency Key"
        )

        logger.error(failure_log)

        return {
            "current_node": "idempotency_node",
            "error_message": (
                "Idempotency node executed "
                "without a valid idempotency key."
            ),
            "workflow_logs": [
                *state["workflow_logs"],
                failure_log
            ]
        }

    # 2. Safe Database Scope
    session = None
    previous_decision = None

    try:
        # Open connection
        session = SessionLocal()
        
        refund_repo = RefundRepository(
            session=session
        )

        # Query the database
        previous_decision = (
            refund_repo.get_previous_decision(
                idempotency_key
            )
        )

    except Exception as e:
        
        failure_log = (
            f"Idempotency Node | "
            f"Status=CRITICAL_DB_FAILURE | "
            f"{ctx} | "
            f"Error={str(e)}"
        )
        
        logger.error(failure_log)
        
        return {
            "current_node": "idempotency_node",
            "error_message": (
                "Database query failed while checking idempotency."
            ),
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
    if previous_decision:

        replay_log = (
            f"Idempotency Node | "
            f"Status=REPLAY_DETECTED | "
            f"{ctx} | "
            f"PreviousStatus="
            f"{previous_decision.status.value.upper()}"
        )

        logger.warning(replay_log)

        return {
            "current_node": "idempotency_node",
            "policy_decision": previous_decision,
            "workflow_logs": [
                *state["workflow_logs"],
                replay_log
            ]
        }

    miss_log = (
        f"Idempotency Node | "
        f"Status=MISS | "
        f"{ctx}"
    )

    logger.info(miss_log)

    return {
        "current_node": "idempotency_node",
        "workflow_logs": [
            *state["workflow_logs"],
            miss_log
        ]
    }