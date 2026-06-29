from pydantic import BaseModel
from typing import Optional, Dict, Any, Literal


class AccountAgentResponse(BaseModel):

    # ---------- Metadata ----------
    ticket_id: str
    customer_id: Optional[int]

    workflow_id: str
    correlation_id: str

    agent_name: Literal["account_agent"] = "account_agent"

    # ---------- Classification ----------
    sub_category: Optional[str]

    requested_action: Optional[str]

    # ---------- Decision ----------
    status: Literal[
        "completed",
        "denied",
        "escalated",
        "clarification_required"
    ]

    decision_reason: Optional[str]

    duration_ms: Optional[int] = None
    
    verification_level: Optional[str]

    risk_level: Optional[str]

    # ---------- Execution ----------
    execution_success: bool

    provider_name: Optional[str]

    provider_status: Optional[str]

    provider_response: Optional[Dict[str, Any]]

    # ---------- Customer Response ----------
    customer_response: str

    # ---------- Escalation ----------
    escalation_required: bool

    security_escalation: bool

    escalation_reason: Optional[str]

    # ---------- Audit ----------
    audit_decision: Optional[str]

    audit_logged: bool