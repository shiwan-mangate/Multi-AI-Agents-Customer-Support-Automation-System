from datetime import datetime, UTC
from decimal import Decimal
from typing import List, Dict, Any, Optional, Literal

from pydantic import BaseModel, Field, EmailStr, ConfigDict


class EventMetadata(BaseModel):
    event_id: str = Field(..., description="Unique event UUID for idempotency")
    event_type: str = Field(..., description="ticket.resolved / ticket.failed / ticket.escalated")
    source_agent: str = Field(
        ...,
        description="faq_agent, refund_agent, account_agent, escalation_agent"
    )
    schema_version: str = Field(default="1.0.0")
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class TicketMetadata(BaseModel):
    ticket_id: str
    workflow_id: Optional[str] = Field(
        default=None,
        description="Workflow/thread identifier"
    )
    trace_id: Optional[str] = Field(
        default=None,
        description="Distributed trace ID"
    )
    channel: str = Field(
        default="web",
        description="web, email, whatsapp, api"
    )


class CustomerMetadata(BaseModel):
    customer_id: int
    customer_email: Optional[EmailStr] = None
    tier: str = Field(
        default="standard",
        description="standard, premium, enterprise"
    )
    ltv: Decimal = Field(
        default=Decimal("0.00"),
        description="Customer lifetime value"
    )
    language: str = Field(
        default="en",
        description="ISO language code"
    )


class ResolutionMetadata(BaseModel):
    status: Literal[
        "resolved",
        "escalated",
        "denied",
        "failed",
        "clarification_required",
        "duplicate_suppressed",
        "human_review_required",
    ]

    resolution_type: str = Field(
        ...,
        description="faq_answer, refund_completed, password_reset, escalation_created"
    )

    resolution_message: Optional[str] = None

    resolved_by: str = Field(
        ...,
        description="Agent or human reviewer"
    )

    time_to_resolution_ms: Optional[int] = Field(
        default=None,
        description="Processing duration in milliseconds"
    )


class RiskMetadata(BaseModel):
    escalated: bool = False
    security_flag: bool = False
    legal_flag: bool = False
    human_review_required: bool = False

    risk_level: Literal[
        "low",
        "medium",
        "high",
        "urgent"
    ] = "low"


class FinancialMetadata(BaseModel):
    refund_amount: Optional[Decimal] = Field(
        default=None,
        decimal_places=2
    )

    currency: Optional[str] = "USD"

    transaction_id: Optional[str] = None


class DecisionMetadata(BaseModel):
    decision_code: Optional[str] = None
    decision_reason: Optional[str] = None

    verification_level: Optional[str] = Field(
        default=None,
        description="PASSED / PARTIAL / FAILED / 2FA_VERIFIED"
    )

    review_required: bool = False
    human_override: bool = False


class AnalyticsMetadata(BaseModel):
    intent: Optional[str] = None

    issue_tags: List[str] = Field(default_factory=list)

    priority: Optional[str] = None

    sla_hours: Optional[int] = None

    feedback: Optional[str] = None

    sentiment_start: Optional[str] = None
    sentiment_end: Optional[str] = None


class ConversationMetadata(BaseModel):
    messages: List[Dict[str, Any]] = Field(default_factory=list)

    agents_involved: List[str] = Field(default_factory=list)

    original_message: Optional[str] = None
    translated_message: Optional[str] = None


class CRMResolvedEvent(BaseModel):
    """
    Canonical CRM event contract.
    All specialist outputs must normalize into this schema.
    """

    model_config = ConfigDict(from_attributes=True)

    event: EventMetadata
    ticket: TicketMetadata
    customer: CustomerMetadata
    resolution: ResolutionMetadata
    risk: RiskMetadata

    financial: Optional[FinancialMetadata] = None
    decision: Optional[DecisionMetadata] = None
    analytics: Optional[AnalyticsMetadata] = None
    conversation: Optional[ConversationMetadata] = None