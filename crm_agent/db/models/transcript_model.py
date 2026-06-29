from datetime import datetime, UTC

from sqlalchemy import String, Integer, DateTime, Text, Index, BigInteger
from sqlalchemy.dialects.postgresql import JSONB, ARRAY
from sqlalchemy.orm import Mapped, mapped_column

from crm_agent.db.base import Base


class TranscriptRecord(Base):
    """
    Immutable append-only audit transcript ledger.
    """

    __tablename__ = "ticket_transcripts"

    __table_args__ = (
        Index("idx_transcript_customer", "customer_id", "created_at"),
        Index("idx_transcript_analytics", "intent", "created_at"),
        Index("idx_transcript_agent_perf", "resolved_by", "created_at"),
    )

    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True
    )

    ticket_id: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        index=True
    )

    schema_version: Mapped[str] = mapped_column(
        String(20),
        default="1.0.0",
        nullable=False
    )

    # Inconsistency Fix: Swapped from Integer to BigInteger to match database keys
    customer_id: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False,
        index=True
    )

    source_agent: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True
    )

    workflow_id: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True
    )

    trace_id: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True
    )

    channel: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True
    )

    messages: Mapped[list[dict]] = mapped_column(
        JSONB,
        nullable=False,
        default=list
    )

    agents_involved: Mapped[list[str]] = mapped_column(
        JSONB,
        nullable=False,
        default=list
    )

    original_message: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    translated_message: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    intent: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
        index=True
    )

    priority: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True
    )

    sentiment_start: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True
    )

    sentiment_end: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True
    )

    issue_tags: Mapped[list[str]] = mapped_column(
        ARRAY(String(100)),
        nullable=False,
        default=list
    )

    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True
    )

    resolution_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    resolution_message: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    resolved_by: Mapped[str] = mapped_column(
        String(50),
        nullable=False
    )

    time_to_resolution_ms: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True
    )

    feedback: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
        index=True
    )