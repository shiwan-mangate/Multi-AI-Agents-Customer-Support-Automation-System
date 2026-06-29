from enum import Enum
from typing import Dict, Any, Optional
from datetime import datetime, UTC

from pydantic import BaseModel, Field, ConfigDict


class ActionSubCategory(str, Enum):
    LOGIN_ISSUE = "login_issue"
    BILLING_QUERY = "billing_query"
    SUBSCRIPTION_CHANGE = "subscription_change"
    ACCESS_RESTORATION = "access_restoration"
    SECURITY_ISSUE = "security_issue"


class VerificationLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    FAILED = "FAILED"


class RiskLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class ProviderStatus(str, Enum):
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    TIMEOUT = "TIMEOUT"
    RATE_LIMITED = "RATE_LIMITED"
    UNAVAILABLE = "UNAVAILABLE"


class ActionType(str, Enum):
    PASSWORD_RESET = "password_reset"
    ACCOUNT_UNLOCK = "account_unlock"
    BILLING_EXPLANATION = "billing_explanation"
    INVOICE_RETRIEVAL = "invoice_retrieval"
    PAYMENT_UPDATE_LINK = "payment_update_link"
    SUBSCRIPTION_UPGRADE = "subscription_upgrade"
    SUBSCRIPTION_DOWNGRADE = "subscription_downgrade"
    SUBSCRIPTION_CANCEL = "subscription_cancel"
    SUBSCRIPTION_PAUSE = "subscription_pause"
    ACCESS_SYNC = "access_sync"
    SECURITY_ESCALATION = "security_escalation"


class ProviderResponse(BaseModel):
    provider_name: str
    status: ProviderStatus
    data: Dict[str, Any] = Field(default_factory=dict)
    error_message: Optional[str] = None


class WorkflowLog(BaseModel):
    model_config = ConfigDict(frozen=True)

    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))
    node: str
    message: str
    data: Dict[str, Any] = Field(default_factory=dict)


class RiskAssessment(BaseModel):
    risk_score: float
    risk_level: RiskLevel
    takeover_detected: bool = False
    abuse_detected: bool = False
    signals: Dict[str, Any] = Field(default_factory=dict)


class AccountDecision(BaseModel):
    sub_category: Optional[ActionSubCategory] = None
    requested_action: ActionType
    verification_level: VerificationLevel
    risk_level: RiskLevel
    action_allowed: bool
    decision_reason: str
    escalation_required: bool = False
    security_escalation: bool = False

class SubclassificationResult(BaseModel):
    """
    Structured output contract for account issue subclassification.
    """

    sub_category: Optional[ActionSubCategory] = Field(
        default=None,
        description="Precise account issue subclassification."
    )

    clarification_required: bool = Field(
        default=False,
        description="Whether the issue is too ambiguous to classify safely."
    )

    clarification_question: Optional[str] = Field(
        default=None,
        description="Question to ask if clarification is required."
    )

class IdentityResolutionResult(BaseModel):
    identity_verified: bool
    identity_confidence: float = Field(ge=0.0, le=100.0)
    resolved_customer_id: Optional[int]
    identity_signals: Dict[str, Any] = Field(default_factory=dict)
    verification_level: VerificationLevel

class AbuseAssessment(BaseModel):
    abuse_detected: bool
    abuse_score: float = Field(ge=0.0, le=100.0)
    signals: Dict[str, Any] = Field(default_factory=dict)
    reason: Optional[str] = None

class TakeoverAssessment(BaseModel):
    takeover_detected: bool
    risk_score_modifier: float = Field(ge=0.0, le=100.0)
    signals: Dict[str, Any] = Field(default_factory=dict)
    reason: Optional[str] = None