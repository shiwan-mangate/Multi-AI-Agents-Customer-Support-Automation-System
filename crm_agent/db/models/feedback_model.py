from datetime import datetime, UTC
from sqlalchemy import String, Integer, BIGINT, DateTime, Text, Boolean, Index
from sqlalchemy.orm import Mapped, mapped_column
import uuid
from crm_agent.db.base import Base


class FeedbackSignal(Base):
    """
    Independent customer feedback intelligence store.
    """

    __tablename__ = "feedback_signals"

    __table_args__ = (
        Index("idx_feedback_customer", "customer_id", "created_at"),
        Index("idx_feedback_agent", "source_agent", "rating", "created_at"),
        Index("idx_feedback_ticket", "ticket_id", unique=True),
    )

    feedback_id: Mapped[str] = mapped_column(
        String(64),
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )

    ticket_id: Mapped[str] = mapped_column(
        String(64),
        nullable=False
    )

    # Inconsistency Fix: Updated column definition to BIGINT to map securely with relational records
    customer_id: Mapped[int] = mapped_column(
        BIGINT,
        nullable=False
    )

    source_agent: Mapped[str] = mapped_column(
        String(50),
        nullable=False
    )

    feedback_type: Mapped[str] = mapped_column(
        String(50),
        default="binary",
        nullable=False
    )

    rating: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )

    comment: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    feedback_channel: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True
    )

    resolution_type: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True
    )

    status: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True
    )

    processed_for_churn: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False
    )