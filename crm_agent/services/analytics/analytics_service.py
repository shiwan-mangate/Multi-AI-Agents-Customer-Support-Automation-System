import logging
import uuid

from decimal import Decimal, ROUND_HALF_UP
from datetime import datetime, UTC, timedelta

from crm_agent.repositories.analytics_repository import AnalyticsRepository

from crm_agent.schemas.analytics import (
    AnalyticsSnapshot,
    AgentPerformanceMetrics,
    IntentMetrics,
    RefundMetrics,
    ChurnDistributionMetrics,
)

logger = logging.getLogger(__name__)


class AnalyticsService:
    """
    Read-only DTO mapping layer for Business Intelligence.

    Responsibilities:
    - Query analytics repositories
    - Convert raw SQL results into strict Pydantic schemas
    - Build dashboard snapshots

    This service NEVER performs writes.
    """

    def __init__(
        self,
        analytics_repo: AnalyticsRepository,
    ):
        self.analytics_repo = analytics_repo


    def generate_dashboard_snapshot(
        self,
        days: int = 30,
    ) -> AnalyticsSnapshot:
        """
        Generates a complete dashboard snapshot for the requested time window.
        """

        logger.debug(
            "Generating analytics snapshot | days=%s",
            days,
        )

        agent_rows = (
            self.analytics_repo.get_agent_performance_metrics(
                days
            )
        )

        intent_rows = (
            self.analytics_repo.get_intent_volume_trends(
                days
            )
        )

        churn_data = (
            self.analytics_repo.get_churn_segmentation()
        )

        refund_data = (
            self.analytics_repo.get_refund_financials(
                days
            )
        )

        period_end = datetime.now(UTC)
        period_start = period_end - timedelta(days=days)

        snapshot = AnalyticsSnapshot(
            snapshot_id=str(uuid.uuid4()),
            generated_at=period_end,

            agent_metrics=[
                AgentPerformanceMetrics(
                    agent_name=row["agent_name"],
                    tickets_handled=int(
                        row.get("tickets_handled", 0) or 0
                    ),
                    avg_resolution_time_ms=int(
                        row.get("avg_resolution_time_ms", 0)
                        or 0
                    ),

                    escalation_rate=self._calculate_rate(
                        row.get("escalations", 0),
                        row.get("tickets_handled", 0),
                    ),

                    failure_rate=self._calculate_rate(
                        row.get("failures", 0),
                        row.get("tickets_handled", 0),
                    ),

                    clarification_rate=Decimal("0.00"),
                )
                for row in agent_rows
            ],

            intent_metrics=[
                IntentMetrics(
                    intent=row.get(
                        "intent",
                        "unknown",
                    ),

                    ticket_count=int(
                        row.get("ticket_count", 0)
                        or 0
                    ),

                    period_start=period_start,
                    period_end=period_end,
                )
                for row in intent_rows
            ],

            refund_metrics=RefundMetrics(
                total_refunds=int(
                    refund_data.get(
                        "total_refunds_processed",
                        0,
                    )
                    or 0
                ),

                total_refund_amount=Decimal("0.00"),

                refund_rejections=int(
                    refund_data.get(
                        "refund_rejections",
                        0,
                    )
                    or 0
                ),

                human_review_count=0,
                idempotent_replay_count=0,
            ),

            churn_distribution=ChurnDistributionMetrics(
                low_count=int(
                    churn_data.get("LOW", 0)
                    or 0
                ),
                medium_count=int(
                    churn_data.get("MEDIUM", 0)
                    or 0
                ),
                high_count=int(
                    churn_data.get("HIGH", 0)
                    or 0
                ),
                urgent_count=int(
                    churn_data.get("URGENT", 0)
                    or 0
                ),
            ),

            faq_metrics=None,
            language_metrics=[],
        )

        logger.info(
            "Analytics snapshot generated | snapshot_id=%s",
            snapshot.snapshot_id,
        )

        return snapshot


    def _calculate_rate(
        self,
        subset_count: int,
        total_count: int,
    ) -> Decimal:
        """
        Calculates a ratio safely.

        Example:
        15 / 100 = 0.15
        """

        if not total_count:
            return Decimal("0.00")

        return (
            Decimal(subset_count)
            / Decimal(total_count)
        ).quantize(
            Decimal("0.01"),  # Adjusted quantization constraint to match schema rules precisely
            rounding=ROUND_HALF_UP,
        )