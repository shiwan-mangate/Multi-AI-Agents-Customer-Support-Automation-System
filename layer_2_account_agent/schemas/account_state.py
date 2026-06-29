from typing import TypedDict, Dict, Any, List, Optional
from datetime import datetime

from .domain import (
    ActionSubCategory,
    VerificationLevel,
    ProviderResponse,
    WorkflowLog,
    RiskAssessment,
    AccountDecision,
    AbuseAssessment,
    TakeoverAssessment,
    ActionType
)


class AccountState(TypedDict, total=False):
    # ---------- Input Contract ----------
    ticket: Dict[str, Any]
    entities: Dict[str, Any]
    ticket_id: int
    customer_email: str
    customer_id: Optional[int]

    # ---------- Supervisor / Triage ----------
    initial_intent: str
    initial_urgency: str
    initial_sentiment: str
    supervisor_confidence: float

    customer_tier: str
    ltv: float
    unresolved_repeat_count: int
    total_tickets: int
    total_escalations: int

    final_priority: str
    sla_duration_hours: int
    sla_deadline: datetime

    # ---------- Classification ----------
    sub_category: Optional[ActionSubCategory]
    clarification_required: bool
    clarification_question: Optional[str]

    # ---------- Identity ----------
    identity_verified: bool
    identity_confidence: float
    verification_level: Optional[VerificationLevel]
    resolved_customer_id: Optional[int]
    identity_signals: Dict[str, Any]

    # ---------- Security ----------
    risk_assessment: Optional[RiskAssessment]
    abuse_assessment: Optional[AbuseAssessment]
    takeover_assessment: Optional[TakeoverAssessment]

    escalation_required: bool
    security_escalation: bool
    escalation_reason: Optional[str]

    # ---------- Context ----------
    auth_context: Dict[str, Any]
    billing_context: Dict[str, Any]
    subscription_context: Dict[str, Any]
    access_context: Dict[str, Any]

    # ---------- Action Resolution ----------
    requested_action: Optional[ActionType]

    # ---------- Decision ----------
    decision: Optional[AccountDecision]

    # ---------- Execution ----------
    action_result: Optional[str]
    provider_response: Optional[ProviderResponse]
    idempotency_key: Optional[str]
    idempotency_blocked: bool
    duplicate_cached_response: bool
    # ---------- Final Response ----------
    customer_response: Optional[str]
    # ---------- Observability ----------
    workflow_logs: List[WorkflowLog]
    errors: List[str]
    retry_count: int
    current_node: Optional[str]

    created_at: datetime
    workflow_id: str
    correlation_id: str
    idempotency_blocked: bool