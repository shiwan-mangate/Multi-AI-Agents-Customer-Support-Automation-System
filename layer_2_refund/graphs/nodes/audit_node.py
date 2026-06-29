import logging
import time
from datetime import datetime, timezone

from ..refund_state import (
    RefundState,
    WorkflowMetrics,
)

from ...repositories.refund_repository import (
    RefundRepository,
)
from layer_2_refund.database.session import SessionLocal

logger = logging.getLogger(__name__)

# REMOVED: Global session = SessionLocal() to prevent connection bleeding

def audit_node(state: RefundState):

    decision = state.get("policy_decision")
    request = state.get("request")
    execution = state.get("execution_result")

    id_key = state.get("idempotency_key")
    workflow_id = state.get("workflow_id")

    metrics = state.get("metrics")

    ctx = (
        f"Workflow={workflow_id} | "
        f"Key={id_key} | "
        f"Ticket={request.ticket_id if request else 'N/A'}"
    )

    log_header = (
        f"Audit Node | Status=STARTING | {ctx}"
    )

    last_event = (
        state["workflow_logs"][-1]
        if state.get("workflow_logs")
        else "No workflow history available"
    )

    completed_at = time.time()

    duration_ms = (
        int(
            (completed_at - metrics.started_at)
            * 1000
        )
        if metrics
        else 0
    )

    # 1. State Guard
    if not decision or not request:

        logger.error(
            f"Audit Node | "
            f"Status=ABORTED | "
            f"{ctx} | "
            f"Reason=Missing Decision/Request"
        )

        return {
            "current_node": "audit_node",
            "audit_status": "FAILED",
            "error_message": (
                "Audit persistence aborted due "
                "to incomplete workflow state."
            ),
            "workflow_logs": [
                *state["workflow_logs"],
                (
                    f"Audit Node | "
                    f"Status=ABORTED | "
                    f"{ctx} | "
                    f"Error=Incomplete State"
                )
            ]
        }

    logger.info(log_header)

    # 2. Safe Session Lifecycle
    session = None
    
    try:
        # Open connection only when needed
        session = SessionLocal()

        repo = RefundRepository(
            session=session
        )

        # 🟢 THE FIX: Prevent PostgreSQL ForeignKeyViolation
        # Extract the reason string safely, checking both common property names
        decision_reason = getattr(decision, "decision_reason", getattr(decision, "reason", ""))
        
        safe_order_id = request.order_id
        
        # If the order doesn't exist, we must pass NULL to the database to bypass the foreign key constraint
        if decision.status.value.lower() == "rejected":
            if "does not exist" in str(decision_reason).lower() or "not found" in str(decision_reason).lower():
                logger.warning(f"Audit Node | Nullifying order_id {request.order_id} to prevent DB FK violation.")
                safe_order_id = None

        success = (
            repo.record_final_transaction(
                idempotency_key=id_key,
                order_id=safe_order_id,  # <-- USE SAFE ID HERE
                decision=decision,
                execution_result=execution,
                metadata={
                    "workflow_id": workflow_id,
                    "duration_ms": duration_ms,
                    "completed_at": (
                        datetime.now(
                            timezone.utc
                        ).isoformat()
                    ),
                    "last_node_event": last_event,
                    "current_node": "audit_node",
                    "retry_count": (
                        metrics.retry_count
                        if metrics
                        else 0
                    )
                }
            )
        )

        if not success:
            raise RuntimeError(
                "Repository persistence failed"
            )

        updated_metrics = metrics.model_copy(
            update={
                "completed_at": completed_at,
                "duration_ms": duration_ms
            }
        )

        logger.info(
            f"Audit Node | "
            f"Status=SUCCESS | "
            f"{ctx} | "
            f"Duration={duration_ms}ms"
        )

        return {
            "current_node": "audit_node",
            "audit_status": "SUCCESS",
            "metrics": updated_metrics,
            "workflow_logs": [
                *state["workflow_logs"],
                log_header,
                (
                    f"Audit Node | "
                    f"Status=SUCCESS | "
                    f"{ctx} | "
                    f"Duration={duration_ms}ms | "
                    f"FinalState="
                    f"{decision.status.value.upper()}"
                )
            ]
        }

    except Exception as e:

        logger.critical(
            f"Audit Node | "
            f"Status=CRITICAL_DATABASE_FAILURE | "
            f"{ctx} | "
            f"Error={str(e)}"
        )

        return {
            "current_node": "audit_node",
            "audit_status": "FAILED",
            "error_message": (
                "Critical audit persistence "
                "failure occurred."
            ),
            "workflow_logs": [
                *state["workflow_logs"],
                log_header,
                (
                    f"Audit Node | "
                    f"Status=DATABASE_FAILURE | "
                    f"{ctx}"
                )
            ]
        }
        
    finally:
        # 3. Guaranteed Cleanup
        if session:
            session.close()