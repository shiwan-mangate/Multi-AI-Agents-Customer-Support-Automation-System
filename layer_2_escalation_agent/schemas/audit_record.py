from enum import Enum
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field


class AuditEventType(str, Enum):
    TRIGGER_DETECTED = "trigger_detected"
    DUPLICATE_DETECTED = "duplicate_detected"
    RISK_SCORED = "risk_scored"
    HOLDING_SENT = "holding_sent"
    BRIEF_GENERATED = "brief_generated"
    ROUTING_COMPLETED = "routing_completed"
    NOTIFICATION_ENQUEUED = "notification_enqueued"
    CASE_RESOLVED = "case_resolved"
    CASE_CLOSED = "case_closed"
    ERROR = "error"


class OperatorType(str, Enum):
    AI = "AI"
    HUMAN = "HUMAN"
    SYSTEM = "SYSTEM"


class AuditRecord(BaseModel):
    case_id: str
    ticket_id: Optional[str] = None
    event_type: AuditEventType
    payload: Dict[str, Any] = Field(default_factory=dict)
    operator_type: OperatorType = Field(default=OperatorType.AI)

    class Config:
        use_enum_values = True