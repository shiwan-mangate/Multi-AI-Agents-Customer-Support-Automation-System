from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field

class HumanDecisionType(str, Enum):
    APPROVE = "approve"
    REJECT = "reject"
    OVERRIDE = "override"
    HOLD = "hold"

class HumanDecision(BaseModel):
    decision: HumanDecisionType
    reviewer_id: str = Field(..., description="ID or email of the human taking action")
    notes: Optional[str] = Field(None, description="Optional justification for the decision")
    override_team: Optional[str] = Field(None, description="Used if decision is OVERRIDE")
    override_priority: Optional[str] = Field(None, description="Used if human overrides SLA urgency")