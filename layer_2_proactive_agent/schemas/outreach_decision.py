
from datetime import datetime, UTC
from typing import Optional

from pydantic import (
    BaseModel,
    Field,
    ConfigDict
)
from layer_2_proactive_agent.schemas.enums import (
    OutreachAction,
)


class OutreachDecision(BaseModel):
    """
    Output produced by outreach_decision_node.
    Represents the final workflow decision
    that determines the next graph path.
    """
    model_config = ConfigDict(
        frozen=True,
        json_schema_extra={
            "example": {
                "action": "OUTREACH",
                "reason": "Customer exhibits elevated churn risk.",
                "review_required": False,
                "escalation_reason": None,
                "decided_at": "2026-05-31T20:30:00Z"
            }
        }
    )
    action: OutreachAction = Field(
        ...,
        description="Final orchestration decision."
    )
    reason: str = Field(
        ...,
        description="Business explanation for the selected action."
    )
    review_required: bool = Field(
        default=False,
        description="Whether human review is recommended."
    )
    escalation_reason: Optional[str] = Field(
        default=None,
        description="Reason escalation was selected."
    )
    decided_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="Timestamp when the decision was generated."
    )