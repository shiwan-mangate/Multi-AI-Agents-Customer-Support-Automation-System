from datetime import datetime, UTC
from typing import List, Optional, Literal

from pydantic import BaseModel, Field, ConfigDict


class MessageMetadata(BaseModel):
    language: Optional[str] = None
    translated: Optional[bool] = None
    tool_used: Optional[str] = Field(
        default=None,
        description="retrieve_faq_chunks, stripe_refund_api, billing_lookup"
    )


class MessageEntry(BaseModel):
    role: Literal[
        "customer",
        "faq_agent",
        "refund_agent",
        "account_agent",
        "escalation_agent",
        "human_agent",
        "system",
    ]

    content: str

    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(UTC)
    )

    metadata: Optional[MessageMetadata] = None


class ResolutionSummary(BaseModel):
    status: Literal[
        "resolved",
        "escalated",
        "denied",
        "failed",
        "clarification_required",
        "duplicate_suppressed",
        "human_review_required",
    ]

    resolution_type: str
    resolution_message: Optional[str] = None
    resolved_by: str
    time_to_resolution_ms: Optional[int] = None


class TranscriptRecord(BaseModel):
    """
    Immutable append-only audit transcript record.
    Persisted in PostgreSQL.
    """

    model_config = ConfigDict(from_attributes=True)

    id: Optional[int] = Field(default=None, description="Mapped ticket_transcripts.id bigint primary key")
    schema_version: str = "1.0.0"

    ticket_id: str
    customer_id: int

    source_agent: Literal[
        "faq_agent",
        "refund_agent",
        "account_agent",
        "escalation_agent",
    ]

    workflow_id: Optional[str] = None
    trace_id: Optional[str] = None
    channel: Optional[str] = None

    messages: List[MessageEntry] = Field(default_factory=list)

    agents_involved: List[Literal[
        "supervisor",
        "triage_agent",
        "faq_agent",
        "refund_agent",
        "account_agent",
        "escalation_agent",
        "human_agent",
    ]] = Field(default_factory=list)

    original_message: Optional[str] = None
    translated_message: Optional[str] = None

    intent: Optional[str] = None
    priority: Optional[str] = None
    sentiment_start: Optional[str] = None
    sentiment_end: Optional[str] = None

    issue_tags: List[str] = Field(default_factory=list)

    resolution: ResolutionSummary

    feedback: Optional[Literal[
        "thumbs_up",
        "thumbs_down"
    ]] = None

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC)
    )

    # =========================================================================
    # Backwards-Compatible Property Proxies for Flattener Compatibility
    # =========================================================================
    @property
    def status(self) -> str:
        return self.resolution.status

    @status.setter
    def status(self, value: str) -> None:
        self.resolution.status = value

    @property
    def resolution_type(self) -> str:
        return self.resolution.resolution_type

    @resolution_type.setter
    def resolution_type(self, value: str) -> None:
        self.resolution.resolution_type = value

    @property
    def resolution_message(self) -> Optional[str]:
        return self.resolution.resolution_message

    @resolution_message.setter
    def resolution_message(self, value: Optional[str]) -> None:
        self.resolution.resolution_message = value

    @property
    def resolved_by(self) -> str:
        return self.resolution.resolved_by

    @resolved_by.setter
    def resolved_by(self, value: str) -> None:
        self.resolution.resolved_by = value

    @property
    def time_to_resolution_ms(self) -> Optional[int]:
        return self.resolution.time_to_resolution_ms

    @time_to_resolution_ms.setter
    def time_to_resolution_ms(self, value: Optional[int]) -> None:
        self.resolution.time_to_resolution_ms = value