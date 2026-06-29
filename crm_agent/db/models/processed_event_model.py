from datetime import datetime, UTC
from sqlalchemy import String, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from crm_agent.db.base import Base


class ProcessedEvent(Base):
    """
    CRM idempotency tracker.
    Prevents duplicate event processing.
    """
    __tablename__ = "processed_events"

    event_id: Mapped[str] = mapped_column(
        String(64),
        primary_key=True
    )

    processed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False
    )

    result_status: Mapped[str] = mapped_column(
        String(20),
        nullable=False
    )