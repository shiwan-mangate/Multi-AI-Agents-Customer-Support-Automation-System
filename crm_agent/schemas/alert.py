from datetime import datetime, UTC
from decimal import Decimal
from typing import List, Optional, Literal
import uuid

from pydantic import BaseModel, Field, EmailStr, ConfigDict, field_serializer


class AlertContext(BaseModel):
    customer_id: int
    ticket_id: Optional[str] = None
    customer_email: Optional[EmailStr] = None

    tier: Literal[
        "standard",
        "premium",
        "enterprise"
    ] = "standard"

    ltv: Decimal = Field(
        default=Decimal("0.00"),
        decimal_places=2
    )

    source_agent: Optional[Literal[
        "faq_agent",
        "refund_agent",
        "account_agent",
        "escalation_agent"
    ]] = None


class AlertPayload(BaseModel):
    alert_type: Literal[
        "CHURN_RISK",
        "VIP_CHURN_RISK",
        "SECURITY_RISK",
        "LEGAL_RISK",
        "SLA_BREACH",
    ]

    severity: Literal[
        "low",
        "medium",
        "high",
        "urgent"
    ]

    score: Decimal = Field(
        ...,
        decimal_places=2
    )

    reason: str

    risk_reasons: List[str] = Field(default_factory=list)


class AlertRecord(BaseModel):
    """
    Persisted operational alert record.
    """

    model_config = ConfigDict(from_attributes=True)

    alert_id: str = Field(
        default_factory=lambda: str(uuid.uuid4())
    )

    context: AlertContext
    payload: AlertPayload

    alert_status: Literal[
        "OPEN",
        "ACKNOWLEDGED",
        "RESOLVED"
    ] = "OPEN"

    delivery_status: Literal[
        "PENDING",
        "SENT",
        "FAILED"
    ] = "PENDING"

    acknowledged: bool = False
    acknowledged_by: Optional[str] = None
    acknowledged_at: Optional[datetime] = None

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC)
    )

    @field_serializer("created_at", "acknowledged_at")
    def serialize_datetime(self, dt: Optional[datetime]) -> Optional[str]:
        return dt.isoformat() if dt else None

    @field_serializer("payload")
    def serialize_payload(self, payload: AlertPayload) -> dict:
        # Resolves any nested serialization transformations safely while matching internal values
        return payload.model_dump()

    @field_serializer("context")
    def serialize_context(self, context: AlertContext) -> dict:
        return context.model_dump()