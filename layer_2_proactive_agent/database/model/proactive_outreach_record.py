from crm_agent.db.base import Base
from uuid import uuid4
from datetime import datetime, UTC
from sqlalchemy import String, DateTime, Index, BigInteger
from sqlalchemy.orm import Mapped, mapped_column

class ProactiveOutreachRecord(Base):
    """
    Suppression and idempotency registry.

    Prevents duplicate proactive outreach
    within configured suppression windows.
    """

    __tablename__ = "proactive_outreach_registry"

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
    decision: Mapped[str] = mapped_column(
        String(50),
        nullable=False
    )
    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False
    )
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False
    )

    __table_args__ = (
        Index(
            "idx_proactive_customer_signal",
            "customer_id",
            "signal_type"
        ),
        Index(
            "idx_proactive_expires_at",
            "expires_at"
        ),
    )