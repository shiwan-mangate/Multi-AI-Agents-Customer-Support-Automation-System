from enum import Enum
from pydantic import BaseModel, Field

class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent" # FIX: Replaced "critical" with "urgent" to match DB schema

class RiskAssessment(BaseModel):
    score: float = Field(..., ge=0.0, le=100.0, description="Deterministic risk score from 0 to 100.")
    level: RiskLevel = Field(..., description="Categorical risk level.")
    legal_risk: bool = Field(default=False)
    security_risk: bool = Field(default=False)
    churn_risk: bool = Field(default=False)
    sla_risk: bool = Field(default=False)

    class Config:
        use_enum_values = True