from datetime import datetime, UTC
from decimal import Decimal
from sqlalchemy import String, BIGINT, DateTime, Numeric, Index
from sqlalchemy.dialects.postgresql import JSONB, ARRAY
from sqlalchemy.orm import Mapped, mapped_column
from crm_agent.db.base import Base


class CustomerProfile(Base):
    """
    Mutable CRM customer intelligence profile.
    Updated atomically via PostgreSQL UPSERT.
    """

    __tablename__ = "customer_support_profiles"

    __table_args__ = (
        Index("idx_customer_churn", "churn_level"),
        Index("idx_customer_last_ticket", "last_ticket_at"),
    )

  
    customer_id: Mapped[int] = mapped_column(
        BIGINT,
        primary_key=True
    )

    customer_email: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        index=True
    )

    tier: Mapped[str] = mapped_column(
        String(50),
        default="standard",
        nullable=False
    )

    ltv: Mapped[Decimal] = mapped_column(
        Numeric,
        default=Decimal("0.00"),
        nullable=False
    )

    total_tickets: Mapped[int] = mapped_column(BIGINT, default=0, nullable=False)
    total_faq_tickets: Mapped[int] = mapped_column(BIGINT, default=0, nullable=False)
    total_refund_tickets: Mapped[int] = mapped_column(BIGINT, default=0, nullable=False)
    total_account_tickets: Mapped[int] = mapped_column(BIGINT, default=0, nullable=False)
    total_escalations: Mapped[int] = mapped_column(BIGINT, default=0, nullable=False)
    total_denials: Mapped[int] = mapped_column(BIGINT, default=0, nullable=False)
    total_failures: Mapped[int] = mapped_column(BIGINT, default=0, nullable=False)
    total_clarifications: Mapped[int] = mapped_column(BIGINT, default=0, nullable=False)
    total_duplicate_suppressions: Mapped[int] = mapped_column(BIGINT, default=0, nullable=False)

    repeat_negative_count: Mapped[int] = mapped_column(BIGINT, default=0, nullable=False)
    repeat_escalation_count: Mapped[int] = mapped_column(BIGINT, default=0, nullable=False)
    duplicate_request_count: Mapped[int] = mapped_column(BIGINT, default=0, nullable=False)
    negative_ticket_count: Mapped[int] = mapped_column(BIGINT, default=0, nullable=False)

    last_sentiment: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True
    )

    sentiment_history: Mapped[list[str]] = mapped_column(
        ARRAY(String(50)),
        default=list,
        nullable=False
    )

    # Inconsistency Fix: Removed precision bounds to mirror database type configurations
    churn_score: Mapped[Decimal] = mapped_column(
        Numeric,
        default=Decimal("0.00"),
        nullable=False
    )

    churn_level: Mapped[str] = mapped_column(
        String(50),
        default="LOW",
        nullable=False,
        index=True
    )

    churn_last_updated: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )

    issue_frequency: Mapped[dict] = mapped_column(
        JSONB,
        default=dict,
        nullable=False
    )

    agent_interaction_frequency: Mapped[dict] = mapped_column(
        JSONB,
        default=dict,
        nullable=False
    )

    languages_used: Mapped[list[str]] = mapped_column(
        ARRAY(String(10)),
        default=list,
        nullable=False
    )

    preferred_language: Mapped[str] = mapped_column(
        String(10),
        default="en",
        nullable=False
    )

    first_seen_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False
    )

    last_ticket_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
        nullable=False
    )
    
    # Matching field setup from initialization scripts
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False
    )