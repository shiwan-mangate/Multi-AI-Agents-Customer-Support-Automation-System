from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field

class EscalationPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent" # FIX: Replaced "critical" with "urgent" to match DB schema

class RoutingDecision(BaseModel):
    assigned_team: str = Field(..., description="Logical human ownership team.")
    target_queue: str = Field(..., description="Operational queue/channel destination.")
    
    risk_level: EscalationPriority = Field(
        ..., 
        description="Escalation urgency level.",
        serialization_alias="risk_level",
        validation_alias="risk_level"
    )
    
    sla_deadline: datetime = Field(..., description="Deadline for human response.")
    routing_reason: str = Field(..., description="Why this routing decision was made.")
    requires_immediate_attention: bool = Field(default=False, description="Whether urgent human intervention is required.")

    class Config:
        use_enum_values = True
        populate_by_name = True