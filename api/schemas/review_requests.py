# api/schemas/review_requests.py
from typing import Optional, Literal
from pydantic import BaseModel, Field


class ReviewActionRequest(BaseModel):
    """
    Payload submitted by a human reviewer
    when resuming a paused workflow.
    """
    reviewer_id: str = Field(...,description="Manager ID, username, or email.")
    decision: Literal[
        "APPROVE",
        "REJECT",
        "REQUEST_CLARIFICATION"
    ] = Field(
        ...,
        description="Final human review decision."
    )
    notes: Optional[str] = Field(
        default=None,
        description="Optional justification or review notes."
    )