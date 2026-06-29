import logging
from decimal import Decimal
from typing import Dict, Any

from crm_agent.services.analytics.analytics_service import (
    AnalyticsService,
)

from crm_agent.schemas.analytics import (
    AnalyticsSnapshot,
)

logger = logging.getLogger(__name__)


class MetricsAggregator:
    """
    Executive KPI aggregation layer.

    Responsibilities:
    - Consume AnalyticsSnapshot.
    - Generate dashboard-friendly KPI payloads.
    - Perform read-only calculations.

    Never:
    - Query SQL directly.
    - Write to the database.
    """

    def __init__(
        self,
        analytics_service: AnalyticsService,
    ):
        self.analytics_service = analytics_service


    def generate_executive_kpis(
        self,
        days: int = 30,
    ) -> Dict[str, Any]:

        logger.debug(
            "Generating executive KPIs | days=%s",
            days,
        )

        snapshot = (
            self.analytics_service.generate_dashboard_snapshot(
                days
            )
        )

        total_tickets = (
            self._calculate_total_volume(
                snapshot
            )
        )

        top_issue = (
            self._determine_top_issue(
                snapshot
            )
        )

        high_risk_customers = (
            self._calculate_risk_exposure(
                snapshot
            )
        )

        leaderboard = (
            self._build_agent_leaderboard(
                snapshot
            )
        )

        refund_rejections = 0

        if snapshot.refund_metrics:
            refund_rejections = (
                snapshot.refund_metrics.refund_rejections
            )

        kpis = {
            "time_window_days": days,
            "generated_at": snapshot.generated_at.isoformat(),

            "total_ticket_volume": total_tickets,

            "high_risk_customers": high_risk_customers,

            "total_refunds": (
                snapshot.refund_metrics.total_refunds
                if snapshot.refund_metrics
                else 0
            ),

            "refund_rejections": refund_rejections,

            "primary_customer_issue": top_issue,

            "agent_performance_ranking": leaderboard,
        }

        logger.info(
            "Executive KPIs generated"
        )

        return kpis


    def _calculate_total_volume(
        self,
        snapshot: AnalyticsSnapshot,
    ) -> int:

        if not snapshot.agent_metrics:
            return 0

        return sum(
            agent.tickets_handled
            for agent in snapshot.agent_metrics
        )

    def _determine_top_issue(
        self,
        snapshot: AnalyticsSnapshot,
    ) -> str:

        if not snapshot.intent_metrics:
            return "No data available"

        top_intent = max(
            snapshot.intent_metrics,
            key=lambda item: item.ticket_count,
        )

        return top_intent.intent

    def _calculate_risk_exposure(
        self,
        snapshot: AnalyticsSnapshot,
    ) -> int:
        if not snapshot.churn_distribution:
            return 0
        return (
            snapshot.churn_distribution.high_count
            + snapshot.churn_distribution.urgent_count
        )

    def _build_agent_leaderboard(
        self,
        snapshot: AnalyticsSnapshot,
    ) -> list[str]:

        if not snapshot.agent_metrics:
            return []

        ranked_agents = sorted(
            snapshot.agent_metrics,
            key=lambda agent: agent.tickets_handled,
            reverse=True,
        )

        return [
            f"{agent.agent_name} ({agent.tickets_handled} tickets)"
            for agent in ranked_agents
        ]