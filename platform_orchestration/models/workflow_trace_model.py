# platform_orchestration/models/workflow_trace_model.py
from datetime import datetime, UTC
from sqlalchemy import (
    String,
    DateTime,
    BigInteger,
    Index,
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
)
from crm_agent.db.base import Base

class WorkflowTrace(Base):

    __tablename__ = "workflow_trace"

    __table_args__ = (
        Index("idx_trace_ticket", "ticket_id"),
    )

    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True
    )

    ticket_id: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    stage: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False
    )

    details: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC)
    )