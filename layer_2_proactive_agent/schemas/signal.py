from datetime import datetime, UTC
from typing import Any, Dict

from pydantic import BaseModel, Field, ConfigDict, field_validator

from layer_2_proactive_agent.schemas.enums import (
    SignalType,
    SignalSource,
)


class Signal(BaseModel):
    """
    Business entry contract for the Proactive Agent (Layer 2).
    A Signal represents a validated proactive trigger entering 
    the orchestration workflow.

    Verified against DB constraints:
    - customer_id -> bigint (Python int handles safely)
    - signal_id -> character varying (str)
    """

    model_config = ConfigDict(
        frozen=True,
        json_schema_extra={
            "example": {
                "signal_id": "SIG-101",
                "customer_id": 123,
                "signal_type": "HIGH_CHURN_RISK",
                "signal_source": "CRM",
                "signal_context": {
                    "churn_score": 89
                },
                "detected_at": "2026-05-31T20:30:00Z"
            }
        }
    )

    signal_id: str = Field(..., description="Unique string-based signal identifier.")
    customer_id: int = Field(..., description="Customer primary key from CRM matching DB bigint type.")
    signal_type: SignalType = Field(..., description="Detected proactive signal category.")
    signal_source: SignalSource = Field(default=SignalSource.CRM, description="Originating source of the signal.")
    signal_context: Dict[str, Any] = Field(
        default_factory=dict,
        description=(
            "Flexible metadata attached to the signal. "
            "Examples: churn_score, ticket_id, days_inactive."
        )
    )
    detected_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="UTC timestamp when the signal was generated."
    )

    @field_validator("customer_id")
    @classmethod
    def validate_customer_id(cls, value: int) -> int:
        """Customer ID must be a positive integer to comply with database architecture."""
        if value <= 0:
            raise ValueError(
                "customer_id must be greater than zero"
            )
        return value