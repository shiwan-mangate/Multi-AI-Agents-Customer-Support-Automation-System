import time
import uuid


from layer_2_refund.graphs.refund_state import (
    RefundState,
    WorkflowMetrics
)

from layer_2_refund.schemas.refund_models import (
    RefundRequest
)


def create_initial_refund_state(
    request: RefundRequest,
    idempotency_key: str,
) -> RefundState:

    workflow_id = (
        f"WF-{uuid.uuid4().hex[:8]}"
    )

    return {

        "workflow_id": workflow_id,

        "idempotency_key": idempotency_key,

        "state_version": 1,

        "request": request,

        "order_data": None,

        "customer_data": None,

        "policy_decision": None,

        "execution_result": None,

        "human_decision": None,

        "review_status": None,

        "workflow_logs": [
            (
                f"Workflow Initialized | "
                f"Workflow={workflow_id}"
            )
        ],

        "current_node": "START",

        "metrics": WorkflowMetrics(
            started_at=time.time()
        ),

        "audit_status": None,

        "error_message": None
    }