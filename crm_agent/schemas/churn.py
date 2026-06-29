from datetime import datetime, UTC
from decimal import Decimal
from typing import List, Optional, Literal

from pydantic import BaseModel, Field, ConfigDict, field_serializer


class ChurnSignalInput(BaseModel):
    """
    Input snapshot for deterministic churn calculation.
    """

    customer_id: int

    ltv: Decimal = Field(
        default=Decimal("0.00"),
        decimal_places=2
    )

    total_tickets: int

    # Aligned with customer_support_profiles.negative_ticket_count column
    negative_ticket_count: int = 0
    unresolved_ticket_count: int = 0
    repeat_negative_count: int = 0
    repeat_escalation_count: int = 0
    duplicate_request_count: int = 0

    last_sentiment: Optional[str] = None
    current_sentiment: Optional[str] = None

    sentiment_trend: Literal[
        "improving",
        "stable",
        "declining"
    ] = "stable"

    days_since_last_ticket: int = 0

    security_incident: bool = False
    legal_incident: bool = False
    high_value_customer: bool = False


class ChurnComputationBreakdown(BaseModel):
    """
    Explainable churn scoring receipt.
    """

    negative_ticket_score: Decimal = Decimal("0.00")
    unresolved_score: Decimal = Decimal("0.00")
    sentiment_score: Decimal = Decimal("0.00")
    escalation_score: Decimal = Decimal("0.00")
    inactivity_score: Decimal = Decimal("0.00")
    security_score: Decimal = Decimal("0.00")
    legal_score: Decimal = Decimal("0.00")

    vip_multiplier_applied: Decimal = Decimal("1.00")

    raw_score: Decimal = Decimal("0.00")

    final_score: Decimal = Field(
        ...,
        decimal_places=2
    )


class ChurnAssessment(BaseModel):
    """
    Final churn decision.
    """

    model_config = ConfigDict(from_attributes=True)

    customer_id: int

    churn_score: Decimal = Field(
        ...,
        decimal_places=2
    )

    churn_level: Literal[
        "low",
        "medium",
        "high",
        "urgent"
    ]

    risk_reasons: List[str] = Field(default_factory=list)

    breakdown: ChurnComputationBreakdown

    computed_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC)
    )

    @field_serializer("computed_at")
    def serialize_datetime(self, dt: datetime) -> str:
        return dt.isoformat()

    @field_serializer("breakdown")
    def serialize_breakdown(self, breakdown: ChurnComputationBreakdown) -> dict:
        return breakdown.model_dump()