from enum import Enum
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field


class NotificationChannel(str, Enum):
    DASHBOARD = "dashboard"
    EMAIL = "email"
    SLACK = "slack"
    TELEGRAM = "telegram"
    PAGER = "pager"


class NotificationStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    SENT = "sent"
    FAILED = "failed"


class NotificationJob(BaseModel):
    case_id: str = Field(..., description="Escalation case reference.")
    channel: NotificationChannel
    recipient: str = Field(..., description="Destination queue/email/channel.")
    payload: Dict[str, Any] = Field(..., description="Structured notification payload.")
    status: NotificationStatus = Field(default=NotificationStatus.PENDING)
    retry_count: int = Field(default=0, ge=0)
    last_error: Optional[str] = Field(default=None)

    # Automatically converts enum selections to standard string primitives
    # when staging outbox items inside relational database operations.
    class Config:
        use_enum_values = True