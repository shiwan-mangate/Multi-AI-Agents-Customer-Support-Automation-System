# layer_4_analytics/schemas/intent_metrics.py

from datetime import datetime
from typing import Literal, Optional
from pydantic import BaseModel, Field, ConfigDict, model_validator


Layer1IntentType = Literal["faq", "refund_request", "account_issue", "technical_bug", "angry_complex"]


class IntentMetrics(BaseModel):
    """
    Data contract representing structural traffic volume, proportional distribution, 
    and period-over-period delta trends for a specific Layer 1 intent classification.
    """

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        validate_assignment=True,
        json_schema_extra={
            "example": {
                "intent_name": "faq",
                "ticket_count": 3200,
                "percentage": 65.00,
                "previous_period_count": 3000,
                "growth_rate": 6.67,
                "period_start": "2026-06-01T00:00:00Z",
                "period_end": "2026-06-08T00:00:00Z"
            }
        }
    )

  
    intent_name: Layer1IntentType = Field(
        ...,
        description="The authenticated routing label assigned by the Layer 1 Supervisor Agent"
    )
    ticket_count: int = Field(
        ...,
        ge=0,
        description="Absolute number of customer tickets categorized into this specific intent during the target window"
    )
    percentage: float = Field(
        ...,
        ge=0.0,
        le=100.0,
        description="Proportional share of this intent relative to total support volume handled: (ticket_count / total_tickets) * 100"
    )
    
    
    previous_period_count: int = Field(
        ...,
        ge=0,
        description="Historical absolute ticket count for this specific intent inside the matching preceding window"
    )
    growth_rate: Optional[float] = Field(
        None,
        description="Period-over-period growth or contraction delta percentage. Stored as None if mathematically undefined (cold-start baseline)"
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
    def validate_mathematical_integrity(self) -> "IntentMetrics":
        """
        Validates mathematical proportions and enforces chronological alignment, 
        leaving cold-start policy decisions explicitly to downstream services.
        """
       
        if self.previous_period_count == 0:
            return self

        
        if self.growth_rate is not None:
            expected_growth = round(
                ((self.ticket_count - self.previous_period_count) / self.previous_period_count) * 100.0, 
                2
            )
           
            if abs(self.growth_rate - expected_growth) > 0.1:
                raise ValueError(
                    f"Trend deviation detected in intent '{self.intent_name}': "
                    f"Given growth_rate={self.growth_rate}% does not align with computed formula ({expected_growth}%)."
                )

        
        if self.period_end < self.period_start:
            raise ValueError(
                f"Temporal anomaly in intent '{self.intent_name}': "
                f"period_end ({self.period_end}) cannot be chronologically prior to period_start ({self.period_start})."
            )

        return self