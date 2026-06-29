from datetime import datetime, UTC
from decimal import Decimal
from pydantic import (
    BaseModel,
    Field,
    ConfigDict,
    field_serializer
)
from layer_2_proactive_agent.schemas.enums import (
    RiskLevel,
)


class RiskAssessment(BaseModel):
    """
    Output produced by risk_scoring_node.
    Represents the final business risk evaluation used by outreach_decision_node.

    Verified against DB constraints:
    - computed_at -> timestamp with time zone (Enforced via UTC datetime object)
    """
    model_config = ConfigDict(
        frozen=True,
        json_schema_extra={
            "example": {
                "risk_level": "HIGH",
                "risk_score": 82.50,
                "risk_reasons": [
                    "Customer churn score exceeded threshold.",
                    "Customer has multiple recent negative interactions."
                ],
                "escalation_candidate": True,
                "computed_at": "2026-06-09T10:00:00Z"
            }
        }
    )

    risk_level: RiskLevel = Field(..., description="Final business risk level.")
    risk_score: Decimal = Field(
        ...,
        ge=Decimal("0"),
        le=Decimal("100"),
        decimal_places=2,
        description="Normalized risk score from 0 to 100."
    )

    risk_reasons: list[str] = Field(
        default_factory=list,
        description="Human-readable reasons contributing to the risk score."
    )

    escalation_candidate: bool = Field(
        default=False,
        description="Whether the customer should be considered for escalation."
    )

    computed_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="Timestamp when the risk assessment was generated. Matches timestamp with time zone."
    )

    @field_serializer('risk_score')
    def serialize_risk_score(self, risk_score: Decimal) -> float:
        """Proper Pydantic V2 native field serializer for Decimal types."""
        return float(risk_score)