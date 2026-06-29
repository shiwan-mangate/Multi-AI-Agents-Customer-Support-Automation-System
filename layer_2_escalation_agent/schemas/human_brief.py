from enum import Enum
from typing import List
from pydantic import BaseModel, Field

# FIX: Aligned with strict tickets.sentiment ENUM
class EmotionalState(str, Enum):
    ANGRY = "angry"
    FRUSTRATED = "frustrated"
    NEUTRAL = "neutral"
    POSITIVE = "positive"

# FIX: Changed CRITICAL to URGENT to match global priority ENUMs
class ChurnRiskLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    URGENT = "URGENT" 

class HumanBrief(BaseModel):
    customer_summary: str = Field(...,description="Condensed customer context for human agent.")
    issue_summary: str = Field(...,description="Core issue in concise form.")
    emotional_state: EmotionalState = Field(...,description="Current emotional posture.")
    churn_risk_level: ChurnRiskLevel = Field(...,description="Estimated churn severity.")
    churn_reason: str = Field(...,description="Why churn risk exists.")
    attempted_actions: List[str] = Field(...,description="Automation actions already attempted.")
    blockers: List[str] = Field(...,description="Reasons automation could not proceed.")
    recommended_next_action: str = Field(...,description="Specific human action recommendation.")
    urgency_reason: str = Field(..., description="Why this escalation is urgent.")
    brief_confidence: float = Field(...,ge=0.0,le=1.0,description="Confidence in brief quality.")