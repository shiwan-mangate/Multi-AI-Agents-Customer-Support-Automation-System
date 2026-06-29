import time

from typing import Optional, List

from pydantic import BaseModel, Field
from typing_extensions import TypedDict


from layer_2_refund.schemas.refund_models import (
    RefundRequest,
    OrderData,
    CustomerData,
    PolicyDecision,
    RefundExecutionResult
)


class WorkflowMetrics(BaseModel):

    started_at: float = Field(
        default_factory=time.time
    )

    completed_at: Optional[float] = None

    duration_ms: Optional[int] = None

    retry_count: int = 0


class RefundState(TypedDict):

    workflow_id: str

    idempotency_key: str

    state_version: int

    request: RefundRequest

    order_data: Optional[OrderData]

    customer_data: Optional[CustomerData]

    policy_decision: Optional[PolicyDecision]

    review_status: Optional[str]

    execution_result: Optional[
        RefundExecutionResult
    ]

    human_decision: Optional[str]

    workflow_logs: List[str]

    current_node: Optional[str]

    metrics: WorkflowMetrics

    audit_status: Optional[str]

    error_message: Optional[str]