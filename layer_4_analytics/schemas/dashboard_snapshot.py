# layer_4_analytics/schemas/dashboard_snapshot.py

from datetime import datetime, timezone
from pydantic import BaseModel, Field, ConfigDict, model_validator

# Phase 1 Sibling Data Contracts Integration
from layer_4_analytics.schemas.agent_metrics import AgentMetrics
from layer_4_analytics.schemas.intent_metrics import IntentMetrics
from layer_4_analytics.schemas.satisfaction_metrics import SatisfactionMetrics
from layer_4_analytics.schemas.churn_metrics import ChurnMetrics
from layer_4_analytics.schemas.roi_metrics import ROIMetrics
from layer_4_analytics.schemas.language_metrics import LanguageMetrics
from layer_4_analytics.schemas.knowledge_gap import KnowledgeGap
from typing import Optional

class DashboardSnapshot(BaseModel):
    """
    The root public API contract, aggregate payload, and master delivery envelope for Layer 4.
    Encapsulates complete business intelligence, system performance ratios, financial ROI,
    and customer health matrices compiled over a specific, unified tracking window.
    """

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        validate_assignment=True,
        json_schema_extra={
            "example": {
                "snapshot_id": "snap_20260611_hourly",
                "generated_at": "2026-06-11T10:45:00Z",
                "report_period_start": "2026-06-01T00:00:00Z",
                "report_period_end": "2026-06-30T23:59:59Z",
                "total_tickets": 3241,
                "total_customers": 812,
                "agent_metrics": [],
                "intent_metrics": [],
                "satisfaction_metrics": None,
                "roi_metrics": None,
                "language_metrics": [],
                "high_risk_customers": [],
                "knowledge_gaps": []
            }
        }
    )

    # --- Metadata tracking & Timeline Authority ---
    snapshot_id: str = Field(
        ...,
        min_length=3,
        description="Unique tracking token identifying this specific historical state capture"
    )
    generated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="The exact timezone-aware UTC execution timestamp recording when this entire state snapshot was compiled"
    )
    report_period_start: datetime = Field(
        ...,
        description="The master timezone-aware UTC lower-bound timestamp governing this entire dashboard data slice"
    )
    report_period_end: datetime = Field(
        ...,
        description="The master timezone-aware UTC upper-bound timestamp governing this entire dashboard data slice"
    )

    # --- Top-Level Dashboard Hero Metrics ---
    total_tickets: int = Field(
        default=0,
        ge=0,
        description="Root-level aggregate of all tickets processed during this window for fast UI rendering"
    )
    total_customers: int = Field(
        default=0,
        ge=0,
        description="Root-level aggregate of distinct active customers during this window for fast UI rendering"
    )

    # --- Domain Metric Aggregations ---
    agent_metrics: list[AgentMetrics] = Field(
        default_factory=list,
        description="List detailing performance, processing speeds, and utilization scores of specialist agents"
    )
    intent_metrics: list[IntentMetrics] = Field(
        default_factory=list,
        description="List tracking absolute volumes and proportional shares across Layer 1 intent classes"
    )
    satisfaction_metrics: SatisfactionMetrics = Field(
        ...,
        description="Top-level aggregated customer satisfaction metrics, feedback distributions, and rolling trend shifts"
    )
    roi_metrics: Optional[ROIMetrics] = None

    language_metrics: list[LanguageMetrics] = Field(
        default_factory=list,
        description="List representing structural platform language adoption and neural translation success rates"
    )

    # --- Operational Action Intelligence and Risks ---
    high_risk_customers: list[ChurnMetrics] = Field(
        default_factory=list,
        description="Customer risk health grid listing specific accounts trending near active attrition boundaries"
    )
    knowledge_gaps: list[KnowledgeGap] = Field(
        default_factory=list,
        description="List of grouped failure categories, customer question examples, and suggested article titles"
    )

    @model_validator(mode="after")
    def validate_snapshot_and_temporal_alignment(self) -> "DashboardSnapshot":
        """
        Enforces global timeline data consistency across aggregated metric boundaries,
        ensuring all timeline fields use timezone-aware UTC timestamps and match the master timeframe.
        """
        # 1. Enforce Strict Timezone-Aware UTC Bounds on the Root Trackers
        for dt_field, dt_val in [
            ("generated_at", self.generated_at),
            ("report_period_start", self.report_period_start),
            ("report_period_end", self.report_period_end)
        ]:
            if dt_val.tzinfo is None:
                raise ValueError(
                    f"Data boundary anomaly in snapshot '{self.snapshot_id}': "
                    f"'{dt_field}' must be explicitly instantiated as a timezone-aware datetime object."
                )
            if dt_val.utcoffset() != timezone.utc.utcoffset(dt_val):
                raise ValueError(
                    f"Data boundary anomaly in snapshot '{self.snapshot_id}': "
                    f"'{dt_field}' uses a non-UTC offset. All Layer 4 metrics must be strictly UTC normalized."
                )

        if self.report_period_end < self.report_period_start:
            raise ValueError(
                f"Temporal chronological inversion in snapshot '{self.snapshot_id}': "
                f"report_period_end cannot occur prior to report_period_start."
            )

        # 2. Advanced Bounding Guard: Cross-Metric Alignment Verification
        target_start = self.report_period_start
        target_end = self.report_period_end

        for am in self.agent_metrics:
            if am.period_start != target_start or am.period_end != target_end:
                raise ValueError(
                    f"Temporal alignment variance in snapshot '{self.snapshot_id}': AgentMetrics for '{am.agent_name}' "
                    f"tracks dates ({am.period_start} -> {am.period_end}) that do not align with the master snapshot window."
                )

        for im in self.intent_metrics:
            if im.period_start != target_start or im.period_end != target_end:
                raise ValueError(
                    f"Temporal alignment variance in snapshot '{self.snapshot_id}': IntentMetrics for '{im.intent_name}' "
                    f"tracks dates ({im.period_start} -> {im.period_end}) that do not align with the master snapshot window."
                )

        if self.satisfaction_metrics.period_start != target_start or self.satisfaction_metrics.period_end != target_end:
            raise ValueError(
                f"Temporal alignment variance in snapshot '{self.snapshot_id}': SatisfactionMetrics "
                f"tracks dates ({self.satisfaction_metrics.period_start} -> {self.satisfaction_metrics.period_end}) "
                f"that do not align with the master snapshot window."
            )

        if self.roi_metrics is not None:
            if (
                self.roi_metrics.period_start != target_start
                or self.roi_metrics.period_end != target_end
            ):
                raise ValueError(
                    f"Temporal alignment variance in snapshot '{self.snapshot_id}': "
                    f"ROIMetrics snapshot tracks dates "
                    f"({self.roi_metrics.period_start} -> {self.roi_metrics.period_end}) "
                    f"that do not align with the master snapshot window."
                )

        for lm in self.language_metrics:
            if lm.period_start != target_start or lm.period_end != target_end:
                raise ValueError(
                    f"Temporal alignment variance in snapshot '{self.snapshot_id}': LanguageMetrics for '{lm.language_code}' "
                    f"tracks dates ({lm.period_start} -> {lm.period_end}) that do not align with the master snapshot window."
                )

        return self