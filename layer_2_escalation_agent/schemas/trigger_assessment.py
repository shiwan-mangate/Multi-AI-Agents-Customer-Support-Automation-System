from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field


class TriggerCategory(str, Enum):
    LEGAL = "legal"
    SECURITY = "security"
    CHURN = "churn"
    SLA = "sla"
    KNOWLEDGE_GAP = "knowledge_gap"
    MANUAL_REVIEW = "manual_review"
    REPEAT_ISSUE = "repeat_issue"
    OPERATIONAL = "operational"
    GENERAL = "general"


class TriggerReason(str, Enum):
    LEGAL_LANGUAGE = "legal_language"
    VIP_AT_RISK = "vip_at_risk"
    TAKEOVER_SUSPICION = "takeover_suspicion"
    IDENTITY_VERIFICATION_FAILED = "identity_verification_failed"
    KNOWLEDGE_GAP_DETECTED = "knowledge_gap_detected"
    LOW_CONFIDENCE = "low_confidence"
    HIGH_VALUE_REFUND = "high_value_refund"
    POLICY_CONFLICT = "policy_conflict"
    SLA_BREACH_IMMINENT = "sla_breach_imminent"
    REPEAT_ISSUE_DETECTED = "repeat_issue_detected"
    DUPLICATE_ESCALATION_DETECTED = "duplicate_escalation_detected"
    CHURN_THREAT = "churn_threat"
    HOSTILE_LANGUAGE = "hostile_language"
    FRAUD_SUSPICION = "fraud_suspicion"
    ACCOUNT_ABUSE_DETECTED = "account_abuse_detected"


class TriggerAssessment(BaseModel):
    # Aligned with the 'trigger_category' column in the escalation_cases table schema
    category: TriggerCategory = Field(
        ...,
        description="Primary escalation category.",
        serialization_alias="trigger_category",
        validation_alias="trigger_category"
    )
    
    # Aligned with the 'trigger_reasons' JSONB column in the escalation_cases table schema
    reasons: List[TriggerReason] = Field(
        ...,
        description="Structured trigger reasons detected.",
        serialization_alias="trigger_reasons",
        validation_alias="trigger_reasons"
    )
    
    duplicate_case_detected: bool = Field(default=False, description="Whether an unresolved escalation already exists.")
    
    # Refactored: Aligned with the 'duplicate_of_case_id' column in the escalation_cases table schema
    existing_case_id: Optional[str] = Field(
        default=None,
        description="Existing active escalation case if duplicate.",
        serialization_alias="duplicate_of_case_id",
        validation_alias="duplicate_of_case_id"
    )

    # Enforces automatic rendering of enum objects directly to text strings 
    # and handles matching across database-sourced dict transformations.
    class Config:
        use_enum_values = True
        populate_by_name = True