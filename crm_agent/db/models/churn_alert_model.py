from datetime import datetime, UTC
from decimal import Decimal
import uuid

from sqlalchemy import String, BIGINT, DateTime, Numeric, Text, Boolean, Index
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, mapped_column

from crm_agent.db.base import Base


class ChurnAlert(Base):
    """
    Persistent operational risk alert ledger.
    """

    __tablename__ = "churn_alerts"

    __table_args__ = (
        Index("idx_alert_suppression", "customer_id", "alert_status", "created_at"),
        Index("idx_alert_delivery", "delivery_status", "created_at"),
        Index("idx_alert_ops_dashboard", "alert_status", "severity"),
    )

    alert_id: Mapped[str] = mapped_column(
        String(64),
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )

    # Inconsistency Fix: Updated from Integer to BIGINT to match schema tracking ledger
    customer_id: Mapped[int] = mapped_column(
        BIGINT,
        nullable=False,
        index=True
    )

    ticket_id: Mapped[str | None] = mapped_column(
        String(64),
        nullable=True
    )

    customer_email: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True
    )

    tier: Mapped[str] = mapped_column(
        String(50),
        default="standard",
        nullable=False
    )

    # Inconsistency Fix: Removed precision bounds to align perfectly with plain numeric schema column type
    ltv: Mapped[Decimal] = mapped_column(
        Numeric,
        default=Decimal("0.00"),
        nullable=False
    )

    source_agent: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True
    )

    alert_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False
    )

    severity: Mapped[str] = mapped_column(
        String(20),
        nullable=False
    )

    # Inconsistency Fix: Removed precision bounds to align with unconstrained numeric column type
    score: Mapped[Decimal] = mapped_column(
        Numeric,
        nullable=False
    )

    reason: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )

    risk_reasons: Mapped[list[str]] = mapped_column(
        ARRAY(String(255)),
        default=list,
        nullable=False
    )

    alert_status: Mapped[str] = mapped_column(
        String(20),
        default="OPEN",
        nullable=False
    )

    delivery_status: Mapped[str] = mapped_column(
        String(20),
        default="PENDING",
        nullable=False
    )

    acknowledged: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False
    )

    acknowledged_by: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True
    )

    acknowledged_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
        nullable=False
    )