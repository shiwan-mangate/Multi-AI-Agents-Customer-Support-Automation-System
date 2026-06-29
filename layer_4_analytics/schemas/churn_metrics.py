# layer_4_analytics/schemas/churn_metrics.py

from datetime import datetime, timezone
from typing import Literal, Union
from pydantic import BaseModel, Field, ConfigDict, model_validator

ChurnRiskTier = Literal["low", "medium", "high"]

RiskDriverType = Literal[
    "negative_sentiment",
    "unresolved_tickets",
    "customer_inactivity",
    "high_escalation_rate",
    "declining_usage"
]


class ChurnMetrics(BaseModel):
    """
    Data contract representing a single customer's predictive churn-risk profile, 
    identifying structural risk drivers, engagement metrics, and sentiment trends.
    """

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        validate_assignment=True,
        json_schema_extra={
            "example": {
                "customer_id": "CUST_1024",
                "customer_name": "Acme Corporation",
                "risk_score": 84.50,
                "risk_level": "HIGH",
                "risk_drivers": [
                    "negative_sentiment",
                    "unresolved_tickets",
                    "customer_inactivity"
                ],
                "last_sentiment_score": -0.72,
                "unresolved_ticket_count": 3,
                "days_since_last_activity": 14,
                "computed_at": "2026-06-11T10:09:29Z"
            }
        }
    )

    
    customer_id: Union[str, int] = Field(
        ...,
        description="The unique relational database identifier linking directly back to CRM customer profiles"
    )
    customer_name: str = Field(
        ...,
        description="The human-readable corporate or individual customer name profile used for UI dashboard presentation"
    )


    risk_score: float = Field(
        ...,
        ge=0.0,
        le=100.0,
        description="The computed quantitative risk calculation value running between 0.0 and 100.0"
    )
    risk_level: ChurnRiskTier = Field(
        ...,
        description="The derived business severity label mapped directly from the computed score category"
    )
    risk_drivers: list[RiskDriverType] = Field(
        ...,
        description="List of validated systemic risk classification keys triggering the elevated score"
    )


    last_sentiment_score: float = Field(
        ...,
        ge=-1.0,
        le=1.0,
        description="Standardized rolling customer sentiment score spanning from -1.0 (volatile/angry) to +1.0 (highly positive)"
    )
    unresolved_ticket_count: int = Field(
        ...,
        ge=0,
        description="Total absolute number of active in-flight tickets currently lingering un-remediated within the system"
    )
    days_since_last_activity: int = Field(
        ...,
        ge=0,
        description="Engagement tracker logging consecutive days since the last recorded user product interaction"
    )

 
    computed_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="The exact timezone-aware UTC timestamp tracking when this health snapshot was compiled"
    )

    @model_validator(mode="after")
    def validate_risk_classification_consistency(self) -> "ChurnMetrics":
        """
        Enforces structural consistency between the quantitative risk score range
        and the business classification tier, keeping business math isolated to services.
        """
     
        if self.risk_score <= 30.0:
            expected_tier = "low"
        elif self.risk_score <= 60.0:
            expected_tier = "medium"
        else:
            expected_tier = "high"

        if self.risk_level != expected_tier:
            raise ValueError(
                f"Risk classification mismatch for customer '{self.customer_name}': "
                f"A risk_score of {self.risk_score} maps to a '{expected_tier}' tier, "
                f"but risk_level was reported as '{self.risk_level}'."
            )


        if self.risk_level in ["medium", "high"] and not self.risk_drivers:
            raise ValueError(
                f"Actionability deficit: Customer account '{self.customer_name}' registers an elevated "
                f"risk_level of '{self.risk_level}', but risk_drivers selection list is empty."
            )

        return self