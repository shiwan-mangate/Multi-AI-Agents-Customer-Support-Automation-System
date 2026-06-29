# layer_4_analytics/schemas/agent_metrics.py

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict, model_validator


class AgentMetrics(BaseModel):
    """
    Data contract representing the operational and customer satisfaction 
    performance KPIs for a single specialist agent within a tracking window.
    """
    
    # Modern Pydantic v2 Configuration
    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        validate_assignment=True,
        json_schema_extra={
            "example": {
                "agent_name": "faq_agent",
                "tickets_handled": 1500,
                "resolved_count": 1371,
                "escalated_count": 129,
                "resolution_rate": 91.40,
                "escalation_rate": 8.60,
                "avg_resolution_time_seconds": 1.15,
                "satisfaction_rate": 88.20,
                "period_start": "2026-06-01T00:00:00Z",
                "period_end": "2026-06-08T00:00:00Z"
            }
        }
    )


    agent_name: str = Field(
        ..., 
        description="The unique identifier string of the specialist agent (e.g., 'faq_agent', 'refund_agent')"
    )
    tickets_handled: int = Field(
        ..., 
        ge=0, 
        description="Total volume of tickets touched by this specific agent within the timeframe"
    )
    resolved_count: int = Field(
        ..., 
        ge=0, 
        description="Number of tickets successfully resolved autonomously by this agent"
    )
    escalated_count: int = Field(
        ..., 
        ge=0, 
        description="Number of tickets blocked and handoff-escalated to human teams or Layer 2 Escalation"
    )
    
  
    resolution_rate: float = Field(
        ..., 
        ge=0.0, 
        le=100.0, 
        description="Percentage calculation representing resolved_count out of total handled volume"
    )
    escalation_rate: float = Field(
        ..., 
        ge=0.0, 
        le=100.0, 
        description="Percentage calculation representing escalated_count out of total handled volume"
    )
    avg_resolution_time_seconds: float = Field(
        ..., 
        ge=0.0, 
        description="The arithmetic mean time in seconds from ticket ingestion to execution termination"
    )
    satisfaction_rate: float = Field(
        ..., 
        ge=0.0, 
        le=100.0, 
        description="The rolling customer CSAT ratio based explicitly on valid positive feedback (👍) flags"
    )
    
   
    period_start: datetime = Field(
        ..., 
        description="The isolation timestamp lower-bound of the analytics compilation window"
    )
    period_end: datetime = Field(
        ..., 
        description="The isolation timestamp upper-bound of the analytics compilation window"
    )

    @property
    def unresolved_count(self) -> int:
        """
        Dynamically derived property tracking in-flight support tickets 
        (e.g., OPEN, IN_PROGRESS, WAITING_CUSTOMER) or data discrepancies.
        """
        return self.tickets_handled - (self.resolved_count + self.escalated_count)

    @model_validator(mode="after")
    def validate_volumetric_integrity(self) -> "AgentMetrics":
        """
        Enforces strict mathematical conservation laws across ticket outcome state transitions,
        while ensuring computed rates align with absolute unit quantities.
        """
       
        combined_actions = self.resolved_count + self.escalated_count
        if combined_actions > self.tickets_handled:
            raise ValueError(
                f"Volumetric anomaly detected in agent '{self.agent_name}': "
                f"Combined outcomes ({combined_actions}) exceed total handled volume ({self.tickets_handled})."
            )

       
        if self.tickets_handled > 0:
            expected_res_rate = round((self.resolved_count / self.tickets_handled) * 100.0, 2)
            expected_esc_rate = round((self.escalated_count / self.tickets_handled) * 100.0, 2)
            
           
            if abs(self.resolution_rate - expected_res_rate) > 0.5:
                raise ValueError(
                    f"Rate divergence in '{self.agent_name}': Given resolution_rate={self.resolution_rate}% "
                    f"does not match calculated proportion ({expected_res_rate}%)."
                )
            if abs(self.escalation_rate - expected_esc_rate) > 0.5:
                raise ValueError(
                    f"Rate divergence in '{self.agent_name}': Given escalation_rate={self.escalation_rate}% "
                    f"does not match calculated proportion ({expected_esc_rate}%)."
                )

      
        if self.period_end < self.period_start:
            raise ValueError(
                f"Temporal anomaly in '{self.agent_name}': "
                f"period_end ({self.period_end}) cannot be chronologically prior to period_start ({self.period_start})."
            )

        return self