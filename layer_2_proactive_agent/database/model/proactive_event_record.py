from datetime import datetime, UTC
from uuid import uuid4

from sqlalchemy import (
    String,
    DateTime,
    BigInteger,
    Index
)

from sqlalchemy.orm import (
    Mapped,
    mapped_column
)

from crm_agent.db.base import Base


class ProactiveEventRecord(Base):
    """
    Audit and analytics record for
    completed proactive workflows.
    """

    __tablename__ = "proactive_events"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid4())
    )

    workflow_id: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    signal_id: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    customer_id: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False
    )

    signal_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    risk_level: Mapped[str] = mapped_column(
        String(50),
        nullable=False
    )

    decision: Mapped[str] = mapped_column(
        String(50),
        nullable=False
    )

    crm_event_id: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False
    )

    __table_args__ = (
        Index(
            "idx_proactive_events_customer",
            "customer_id"
        ),
        Index(
            "idx_proactive_events_signal",
            "signal_type"
        ),
        Index(
            "idx_proactive_events_created",
            "created_at"
        ),
    )