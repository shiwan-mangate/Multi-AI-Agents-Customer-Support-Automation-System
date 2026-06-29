from datetime import datetime, UTC
from decimal import Decimal
from typing import List, Literal, Optional
import uuid

from pydantic import BaseModel, Field, ConfigDict, field_serializer


class AgentPerformanceMetrics(BaseModel):
    agent_name: Literal[
        "faq_agent",
        "refund_agent",
        "account_agent",
        "escalation_agent",
    ]

    tickets_handled: int = 0

    # Aligned with ticket_transcripts.time_to_resolution_ms (integer column)
    avg_resolution_time_ms: int = 0

    escalation_rate: Decimal = Field(
        default=Decimal("0.00"),
        decimal_places=2,
        ge=Decimal("0.00"),
        le=Decimal("1.00")
    )

    failure_rate: Decimal = Field(
        default=Decimal("0.00"),
        decimal_places=2,
        ge=Decimal("0.00"),
        le=Decimal("1.00")
    )

    clarification_rate: Decimal = Field(
        default=Decimal("0.00"),
        decimal_places=2,
        ge=Decimal("0.00"),
        le=Decimal("1.00")
    )


class IntentMetrics(BaseModel):
    intent: str
    ticket_count: int = 0
    period_start: datetime
    period_end: datetime


class RefundMetrics(BaseModel):
    total_refunds: int = 0

    total_refund_amount: Decimal = Field(
        default=Decimal("0.00"),
        decimal_places=2
    )

    refund_rejections: int = 0
    human_review_count: int = 0
    idempotent_replay_count: int = 0


class FAQMetrics(BaseModel):
    total_faq_resolved: int = 0
    knowledge_gap_count: int = 0
    clarification_count: int = 0
    retrieval_failure_count: int = 0

    containment_rate: Decimal = Field(
        default=Decimal("0.00"),
        decimal_places=2,
        ge=Decimal("0.00"),
        le=Decimal("1.00")
    )


class AccountMetrics(BaseModel):
    total_account_resolved: int = 0
    security_escalation_count: int = 0
    denial_count: int = 0
    verification_failure_count: int = 0


class EscalationMetrics(BaseModel):
    total_escalations: int = 0
    duplicate_suppressions: int = 0
    human_review_count: int = 0
    override_count: int = 0
    escalation_failures: int = 0


class LanguageMetrics(BaseModel):
    language: str
    ticket_count: int = 0
    translation_count: int = 0


class ChurnDistributionMetrics(BaseModel):
    low_count: int = 0
    medium_count: int = 0
    high_count: int = 0
    urgent_count: int = 0

    computed_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC)
    )


class AnalyticsSnapshot(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    snapshot_id: str = Field(
        default_factory=lambda: str(uuid.uuid4())
    )

    generated_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC)
    )

    agent_metrics: List[AgentPerformanceMetrics] = Field(default_factory=list)
    intent_metrics: List[IntentMetrics] = Field(default_factory=list)

    refund_metrics: Optional[RefundMetrics] = None
    faq_metrics: Optional[FAQMetrics] = None
    account_metrics: Optional[AccountMetrics] = None
    escalation_metrics: Optional[EscalationMetrics] = None

    language_metrics: List[LanguageMetrics] = Field(default_factory=list)

    churn_distribution: ChurnDistributionMetrics

    @field_serializer("generated_at")
    def serialize_datetime(self, dt: datetime) -> str:
        return dt.isoformat()

    @field_serializer("agent_metrics", "intent_metrics", "language_metrics")
    def serialize_lists(self, metrics_list: List[BaseModel]) -> List[dict]:
        return [m.model_dump() for m in metrics_list]

    @field_serializer("refund_metrics", "faq_metrics", "account_metrics", "escalation_metrics", "churn_distribution")
    def serialize_optional_blocks(self, metrics_block: Optional[BaseModel]) -> Optional[dict]:
        return metrics_block.model_dump() if metrics_block else None