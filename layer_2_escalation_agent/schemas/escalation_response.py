from enum import Enum
from pydantic import BaseModel, Field

from .risk_assessment import RiskLevel


class EscalationStatus(str, Enum):
    ESCALATED = "ESCALATED"
    DUPLICATE_SUPPRESSED = "DUPLICATE_SUPPRESSED"
    FAILED = "FAILED"


class EscalationResponse(BaseModel):
    status: EscalationStatus = Field(...,description="Final escalation workflow outcome.")
    case_id: str | None = Field(default=None,description="Escalation tracking case ID.")
    priority: RiskLevel | None = Field(default=None,description="Escalation priority.")
    assigned_team: str | None = Field(default=None,description="Assigned human support team.")
    holding_sent: bool = Field(default=False,description="Whether customer received holding response.")
    error_message: str | None = Field(default=None,description="Failure explanation if workflow failed.")