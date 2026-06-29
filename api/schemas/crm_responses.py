from datetime import datetime
from enum import Enum
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class AlertSeverity(str, Enum):
    """Strict constraints for operational risk levels."""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class CustomerProfileResponse(BaseModel):
    """The central customer representation for the UI."""
    customer_id: int = Field(..., examples=[1])
    customer_email: str = Field(..., examples=["rahul@example.com"])
    tier: str = Field(..., examples=["premium", "standard"])
    ltv: float = Field(..., examples=[1250.00])
    total_tickets: int = Field(..., examples=[14])
    
    churn_score: Optional[float] = Field(None, examples=[0.85])
    churn_level: Optional[str] = Field(None, examples=["HIGH"])
    last_sentiment: Optional[str] = Field(None, examples=["frustrated"])
    negative_ticket_count: int = Field(..., examples=[2])


class TimelineEvent(BaseModel):
    """A unified chronological event (Ticket, Alert, or System Action)."""
    event_id: str = Field(..., description="Stable unique identifier for frontend lists")
    event_type: str = Field(..., description="'transcript', 'alert', or 'action'")
    timestamp: datetime
    title: str
    description: str
    metadata: Dict[str, Any] = Field(default_factory=dict)


class CustomerTimelineResponse(BaseModel):
    """The complete, paginatable history of a customer."""
    customer_id: int = Field(..., examples=[1])
    total_events: int = Field(..., description="Total available events for pagination logic")
    events: List[TimelineEvent]


class ChurnAlertResponse(BaseModel):
    """Represents an active risk warning."""
    alert_id: str
    customer_id: int
    alert_type: str
    severity: AlertSeverity
    reason: str
    status: str
    created_at: datetime