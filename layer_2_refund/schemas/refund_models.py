from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum



# ENUMS (Aligned with DB character varying fields)

class RefundStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    ESCALATED = "escalated"
    COMPLETED = "completed"


class OrderStatus(str, Enum):
    PROCESSING = "PROCESSING"
    SHIPPED = "SHIPPED"
    DELIVERED = "DELIVERED"
    RETURNED = "RETURNED"
    DELAYED = "DELAYED" 


# INPUT SCHEMAS (From Layer 1 / Triage)
class RefundRequest(BaseModel):
    ticket_id: str
    order_id: int
    customer_id: int
    reason_for_refund: str



# DATABASE-MAPPED SCHEMAS (Domain Data)
class OrderData(BaseModel):
    """Maps directly to the 'orders' DB table."""
    order_id: int
    customer_id: int
    order_amount: float = Field(gt=0)
    order_status: OrderStatus
    created_at: datetime
    
    # In-memory only (used by policy rules, not stored in DB)
    is_refundable: Optional[bool] = None


class CustomerData(BaseModel):
    """Maps directly to the 'customers' DB table."""
    customer_id: int
    name: str
    email: str
    account_tier: Optional[str] = Field(
        default="standard",
        description="Customer account tier (e.g., standard, premium)"
    )
    total_spent: Optional[float] = 0.0
    created_at: datetime



# WORKFLOW STATE SCHEMAS (In-Memory & Audit)
class PolicyDecision(BaseModel):
    """Translates to fields in 'processed_refunds' and 'refund_audit'."""
    status: RefundStatus
    code: str = Field(
        ...,
        description="Machine-readable decision code"
    )
    reason: str
    refund_amount: Optional[float] = None
    requires_human_review: bool = False
    metadata: dict = Field(default_factory=dict)


class RefundExecutionResult(BaseModel):
    """In-memory result from the Payment Gateway service."""
    success: bool
    transaction_id: Optional[str] = None
    execution_message: str


class IdempotencyRecord(BaseModel):
    """Maps to the tracking columns in 'processed_refunds'."""
    idempotency_key: str
    order_id: int
    created_at: datetime


# =================================================================
# OUTPUT SCHEMA (Final Agent Payload)
# =================================================================

# layer_2_refund/schemas/refund_models.py

class RefundOutput(BaseModel):
    ticket_id: str
    workflow_id: str
    customer_id: int
    order_id: int
    final_status: RefundStatus
    decision_code: str
    decision_reason: str
    customer_response: Optional[str] = None
    refund_amount: Optional[float] = None
    transaction_id: Optional[str] = None
    review_required: bool = False
    review_status: Optional[str] = None
    
    # FIXED: Added Optional so the model doesn't crash when paused for Human Review
    audit_status: Optional[str] = None 
    
    duration_ms: Optional[int] = None