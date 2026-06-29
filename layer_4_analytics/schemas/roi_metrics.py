# layer_4_analytics/schemas/roi_metrics.py

from datetime import datetime, timezone
from typing import Optional, Union
from pydantic import BaseModel, Field, ConfigDict, model_validator


class ROIMetrics(BaseModel):
    """
    Data contract representing the financial return on investment (ROI), 
    cost savings profiles, and automation efficiency metrics for a specific customer account.
    """

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        validate_assignment=True,
        json_schema_extra={
            "example": {
                "customer_id": "CUST_9941",
                "customer_name": "SaaS Global Corp",
                "total_tickets": 3241,
                "auto_resolved_tickets": 2755,
                "escalated_tickets": 486,
                "auto_resolution_rate": 85.00,
                "estimated_cost_per_ticket": 4.00,
                "gross_savings": 11020.00,
                "platform_cost": 199.00,
                "net_savings": 10821.00,
                "roi_percentage": 5437.69,
                "period_start": "2026-06-01T00:00:00Z",
                "period_end": "2026-06-30T23:59:59Z"
            }
        }
    )

    
    customer_id: Union[str, int] = Field(
        ...,
        description="The unique relational database identifier linking back to the specific client customer profile"
    )
    customer_name: str = Field(
        ...,
        description="The human-readable client corporate name used for executive ROI report rendering"
    )

   
    total_tickets: int = Field(
        ...,
        ge=0,
        description="Total support interaction volume arriving at the platform entry layer for this client"
    )
    auto_resolved_tickets: int = Field(
        ...,
        ge=0,
        description="Absolute number of support tickets successfully resolved by the AI without human touching"
    )
    escalated_tickets: int = Field(
        ...,
        ge=0,
        description="Absolute number of support tickets that required handoff routing to human teams"
    )
    auto_resolution_rate: float = Field(
        ...,
        ge=0.0,
        le=100.0,
        description="Proportional share of AI-resolved tickets out of total load: (auto_resolved_tickets / total_tickets) * 100"
    )

   
    estimated_cost_per_ticket: float = Field(
        ...,
        ge=0.0,
        description="Conservative standard corporate cost parameter for a human support agent to process a single interaction manually"
    )
    gross_savings: float = Field(
        ...,
        ge=0.0,
        description="Total business operating expenses avoided via automated resolution: auto_resolved_tickets * estimated_cost_per_ticket"
    )
    platform_cost: float = Field(
        ...,
        ge=0.0,
        description="The client's fixed monthly subscription cost paid for platform software access"
    )
    net_savings: float = Field(
        ...,
        description="Clear net operating capital saved through automation: gross_savings - platform_cost"
    )
    roi_percentage: Optional[float] = Field(
        ...,
        description="The commercial efficiency ratio representing return on technology investment. Can be float('inf') for free tiers"
    )


    period_start: datetime = Field(
        ...,
        description="The timezone-aware UTC isolation timestamp lower-bound of the financial auditing window"
    )
    period_end: datetime = Field(
        ...,
        description="The timezone-aware UTC isolation timestamp upper-bound of the financial auditing window"
    )

    @model_validator(mode="after")
    def validate_financial_and_volumetric_integrity(self) -> "ROIMetrics":
        """
        Enforces strict mathematical conservation laws across tickets handled, 
        financial savings equations, and timezone-aware chronological reporting bounds.
        """
        
        if (self.auto_resolved_tickets + self.escalated_tickets) != self.total_tickets:
            raise ValueError(
                f"Volumetric imbalance for client '{self.customer_name}': Auto-resolved ({self.auto_resolved_tickets}) + "
                f"escalated ({self.escalated_tickets}) must equal total_tickets ({self.total_tickets})."
            )

        
        if self.total_tickets == 0:
            if self.auto_resolution_rate != 0.0:
                raise ValueError(f"Logical rate conflict for '{self.customer_name}': Total tickets is 0, but auto_resolution_rate is {self.auto_resolution_rate}%.")
        else:
            expected_rate = round((self.auto_resolved_tickets / self.total_tickets) * 100.0, 2)
            if abs(self.auto_resolution_rate - expected_rate) > 0.5:
                raise ValueError(
                    f"Automation metric conflict for '{self.customer_name}': Given auto_resolution_rate={self.auto_resolution_rate}% "
                    f"does not match computed baseline ({expected_rate}%)."
                )

        
        expected_gross = round(self.auto_resolved_tickets * self.estimated_cost_per_ticket, 2)
        if abs(self.gross_savings - expected_gross) > 0.5:
            raise ValueError(
                f"Gross calculation drift for '{self.customer_name}': Stated gross_savings={self.gross_savings} "
                f"differs from expected product value ({expected_gross})."
            )

        expected_net = round(self.gross_savings - self.platform_cost, 2)
        if abs(self.net_savings - expected_net) > 0.5:
            raise ValueError(
                f"Net calculation drift for '{self.customer_name}': Stated net_savings={self.net_savings} "
                f"differs from expected delta subtraction ({expected_net})."
            )

       
        if self.platform_cost == 0.0:
            if self.net_savings > 0.0:
                expected_roi = float("inf")
            else:
                expected_roi = 0.0
                
            if self.roi_percentage != expected_roi:
                raise ValueError(
                    f"Free-tier ROI calculation mismatch for '{self.customer_name}': "
                    f"With zero platform cost and net_savings={self.net_savings}, expected ROI to be {expected_roi}, got {self.roi_percentage}."
                )
        else:
            expected_roi = round((self.net_savings / self.platform_cost) * 100.0, 2)
            if self.roi_percentage is None or abs(self.roi_percentage - expected_roi) > 0.5:
                raise ValueError(
                    f"ROI metrics deviation for '{self.customer_name}': Stated roi_percentage={self.roi_percentage}% "
                    f"does not match computed percentage equation ({expected_roi}%)."
                )

     
        if self.period_start.tzinfo is None or self.period_end.tzinfo is None:
            raise ValueError(
                f"Timezone enforcement violation for '{self.customer_name}': Both period_start and "
                f"period_end must be explicitly instantiated as timezone-aware UTC datetime parameters."
            )
            
        if self.period_end < self.period_start:
            raise ValueError(
                f"Temporal chronological error for '{self.customer_name}': period_end ({self.period_end}) "
                f"cannot occur prior to period_start ({self.period_start})."
            )

        return self