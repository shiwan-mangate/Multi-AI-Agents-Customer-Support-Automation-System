# layer_4_analytics/schemas/satisfaction_metrics.py

from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict, model_validator


class SatisfactionMetrics(BaseModel):
    """
    Data contract representing top-level aggregated Customer Satisfaction (CSAT) KPIs,
    feedback distribution matrices, and period-over-period sentiment trend shifts.
    """

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        validate_assignment=True,
        json_schema_extra={
            "example": {
                "positive_feedback_count": 880,
                "negative_feedback_count": 120,
                "neutral_feedback_count": 0,
                "total_feedback_count": 1000,
                "satisfaction_rate": 88.00,
                "previous_period_rate": 86.00,
                "trend_percentage": 2.00,
                "period_start": "2026-06-01T00:00:00Z",
                "period_end": "2026-06-08T00:00:00Z"
            }
        }
    )

    positive_feedback_count: int = Field(
        ...,
        ge=0,
        description="Total absolute number of positive customer feedback indicators logged (👍)"
    )
    negative_feedback_count: int = Field(
        ...,
        ge=0,
        description="Total absolute number of negative customer feedback indicators logged (👎)"
    )
    neutral_feedback_count: int = Field(
        default=0,
        ge=0,
        description="Future-proofing baseline hook representing neutral feedback responses (😐)"
    )
    total_feedback_count: int = Field(
        ...,
        ge=0,
        description="Aggregated absolute sum total of all feedback interaction records captured"
    )

  
    satisfaction_rate: float = Field(
        ...,
        ge=0.0,
        le=100.0,
        description="Current period customer satisfaction score percentage: (positive_count / total_feedback_count) * 100"
    )
    previous_period_rate: float = Field(
        ...,
        ge=0.0,
        le=100.0,
        description="Historical customer satisfaction score percentage captured inside the matching preceding window"
    )
    trend_percentage: float = Field(
        ...,
        description="Absolute percentage-point delta velocity metric representing CSAT performance shift: current_rate - previous_rate"
    )

    period_start: datetime = Field(
        ...,
        description="The isolation timestamp lower-bound of the analytics compilation window"
    )
    period_end: datetime = Field(
        ...,
        description="The isolation timestamp upper-bound of the analytics compilation window"
    )

    @model_validator(mode="after")
    def validate_satisfaction_mathematical_integrity(self) -> "SatisfactionMetrics":
        """
        Enforces algebraic consistency across raw volume inputs, derivative percentage rates,
        and chronological window context boundaries.
        """
       
        calculated_total = (
            self.positive_feedback_count + 
            self.negative_feedback_count + 
            self.neutral_feedback_count
        )
        if calculated_total != self.total_feedback_count:
            raise ValueError(
                f"Volumetric discrepancy in CSAT tracking: Combined parameters sum to "
                f"{calculated_total}, but total_feedback_count was reported as {self.total_feedback_count}."
            )

     
        if self.total_feedback_count > 0:
            expected_rate = round((self.positive_feedback_count / self.total_feedback_count) * 100.0, 2)
           
            if abs(self.satisfaction_rate - expected_rate) > 0.1:
                raise ValueError(
                    f"CSAT score derivation error: Provided satisfaction_rate={self.satisfaction_rate}% "
                    f"does not match computed target ({expected_rate}%)."
                )

        
        expected_trend = round(self.satisfaction_rate - self.previous_period_rate, 2)
        if abs(self.trend_percentage - expected_trend) > 0.1:
            raise ValueError(
                f"Trend calculation discrepancy: Stated trend_percentage={self.trend_percentage} "
                f"does not match derived subtraction calculation ({expected_trend})."
            )

        # 4. Check time bounding context consistency
        if self.period_end < self.period_start:
            raise ValueError(
                f"Temporal anomaly detected: period_end ({self.period_end}) "
                f"cannot occur chronologically before period_start ({self.period_start})."
            )

        return self