from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any


class PendingReviewItem(BaseModel):
    workflow_id: str
    ticket_id: str
    agent_type: str
    status: str


class PendingReviewsResponse(BaseModel):
    total_pending: int
    reviews: List[PendingReviewItem]


class ReviewOutcomeResponse(BaseModel):
    ticket_id: str
    status: str = Field(...,description="Final workflow status after manager decision.")
    decision_applied: str = Field(...,description="Manager action that was executed." )
    customer_facing_response: Optional[str] = Field(
    default=None,
    description="Customer-facing response generated after workflow resume."
)