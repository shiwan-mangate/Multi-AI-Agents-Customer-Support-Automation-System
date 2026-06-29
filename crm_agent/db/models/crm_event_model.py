from datetime import datetime, UTC
from sqlalchemy import String, Integer, DateTime, Text, Index
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column
from crm_agent.db.base import Base


class CRMEvent(Base):
    """
    PostgreSQL-backed distributed CRM event queue.
    Workers consume rows using FOR UPDATE SKIP LOCKED.
    """

    __tablename__ = "crm_events"

    __table_args__ = (
        Index("idx_crm_queue_polling", "status", "created_at"),
    )

    event_id: Mapped[str] = mapped_column(
        String(64),
        primary_key=True
    )

    event_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True
    )

    source_agent: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True
    )

    schema_version: Mapped[str] = mapped_column(
        String(20),
        default="1.0.0",
        nullable=False
    )

    payload: Mapped[dict] = mapped_column(
        JSONB,
        nullable=False
    )

    status: Mapped[str] = mapped_column(
        String(20),
        default="NEW",
        nullable=False,
        index=True
    )

    retry_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False
    )

    claimed_by: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True
    )

    claimed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
        index=True
    )

    processed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )

    # Added to maintain full compatibility with lifecycle state tracks and cleanup updates
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
        nullable=False
    )

    last_error: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )