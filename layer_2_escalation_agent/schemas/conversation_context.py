from enum import Enum
from typing import List, Dict, Any
from pydantic import BaseModel, Field


class FailureReason(str, Enum):
    KNOWLEDGE_GAP_DETECTED = "knowledge_gap_detected"
    LOW_CONFIDENCE = "low_confidence"
    POLICY_CONFLICT = "policy_conflict"
    FRAUD_SUSPICION = "fraud_suspicion"
    IDENTITY_VERIFICATION_FAILED = "identity_verification_failed"
    TAKEOVER_SUSPICION = "takeover_suspicion"
    MANUAL_REVIEW_REQUIRED = "manual_review_required"
    SLA_BREACH_IMMINENT = "sla_breach_imminent"
    DUPLICATE_ESCALATION_DETECTED = "duplicate_escalation_detected"


class AgentAction(BaseModel):
    agent_name: str
    action: str
    result: str
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ConversationContext(BaseModel):
    conversation_transcript: str = Field(..., description="Flattened customer + bot interaction transcript.")
    agent_actions_taken: List[AgentAction] = Field(default_factory=list, description="Structured list of specialist actions already attempted.")
    failure_reasons: List[FailureReason] = Field(default_factory=list, description="Structured escalation causes.")
    knowledge_gap_detected: bool = Field(default=False, description="Whether FAQ retrieval failed.")


    class Config:
        use_enum_values = True