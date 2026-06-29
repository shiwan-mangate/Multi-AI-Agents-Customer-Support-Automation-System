from datetime import datetime, UTC
from pydantic import (
    BaseModel,
    Field,
    ConfigDict,
    EmailStr
)

class EscalationHandoff(BaseModel):
    """
    Normalized contract used to transfer critical proactive cases 
    into the Escalation Agent workflow (Layer 3).
    
    Verified against DB constraints:
    - ticket_id -> character varying (str)
    - customer_id -> bigint (int)
    """

    model_config = ConfigDict(
        frozen=True,
        json_schema_extra={
            "example": {
                "ticket_id": "SYS-PRO-456",
                "customer_id": 456,
                "customer_email": "vip@enterprise.com",
                "source_agent": "proactive_agent",
                "initial_intent": "angry_complex",
                "initial_sentiment": "angry",
                "initial_urgency": "urgent",
                "supervisor_confidence": 1.0,
                "message_raw": (
                    "SYSTEM TRIGGER: Customer shows "
                    "critical churn risk."
                ),
                "message_english": (
                    "SYSTEM TRIGGER: Customer shows "
                    "critical churn risk."
                ),
                "created_at": "2026-05-31T20:30:00Z"
            }
        }
    )

    ticket_id: str = Field(..., description="System-generated escalation ticket ID matching DB varchar type.")
    customer_id: int = Field(..., description="Customer identifier from CRM matching DB bigint type.")
    customer_email: EmailStr = Field(..., description="Customer email address.")
    source_agent: str = Field(default="proactive_agent", description="Agent creating the escalation.")
    initial_intent: str = Field(..., description="Intent assigned to the escalation.")
    initial_sentiment: str = Field(..., description="Customer sentiment that triggered escalation.")
    initial_urgency: str = Field(..., description="Urgency assigned by proactive risk evaluation.")
    supervisor_confidence: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
        description="Confidence associated with escalation routing."
    )
    repeat_issue_count: int = 0
    knowledge_gap_detected: bool = False
    message_raw: str = Field(..., description="Original escalation message.")
    message_english: str = Field(..., description="English version of escalation message.")
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC), description="UTC timestamp when handoff was created.")