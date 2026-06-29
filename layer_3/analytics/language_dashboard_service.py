import logging
from datetime import datetime, timezone
from typing import Dict, Any

from layer_3.analytics.language_metrics_service import LanguageMetricsService

logger = logging.getLogger(__name__)

class LanguageDashboardService:
    """
    Presentation Layer for Layer 3 Analytics.
    Aggregates business KPIs from the LanguageMetricsService into complete 
    dashboard payloads for UI, Grafana, and Admin APIs.
    """

    def __init__(self, metrics_service: LanguageMetricsService):
        self.metrics_service = metrics_service

    def _get_timestamp(self) -> str:
        """Helper to append generation timestamps for UI staleness tracking."""
        return datetime.now(timezone.utc).isoformat()

    def get_dashboard(self, days: int = 30, failure_limit: int = 100) -> Dict[str, Any]:
        """
        Responsibility 1: Full Dashboard Payload
        Provides a complete snapshot of the translation system's state.
        """
        logger.info(f"LanguageDashboardService | Generating full dashboard payload (days={days})")
        try:
            return {
                "generated_at": self._get_timestamp(),
                "dashboard_type": "full",
                "status": "SUCCESS",
                "executive_summary": self.metrics_service.get_executive_summary(days=days),
                "system_health": self.metrics_service.get_system_health_metrics(),
                "language_usage": self.metrics_service.get_language_usage_metrics(days=days),
                "failure_metrics": self.metrics_service.get_failure_metrics(limit=failure_limit)
            }
        except Exception as e:
            logger.critical(f"LanguageDashboardService | Failed to generate full dashboard: {e}")
            return {
                "generated_at": self._get_timestamp(),
                "dashboard_type": "full",
                "status": "ERROR", 
                "error": str(e)
            }

    def get_operations_dashboard(self, failure_limit: int = 100) -> Dict[str, Any]:
        """
        Responsibility 2: Targeted Operations View
        Focuses exclusively on system health and failure triage for DevOps/SREs.
        """
        logger.info("LanguageDashboardService | Generating operations dashboard payload")
        try:
            health = self.metrics_service.get_system_health_metrics()
            failures = self.metrics_service.get_failure_metrics(limit=failure_limit)
            
            # Surface critical alerts at the top level for Ops monitoring tools
            system_status = health.get("system_health", "UNKNOWN")
            is_alerting = system_status in ["WARNING", "URGENT"]

            return {
                "generated_at": self._get_timestamp(),
                "dashboard_type": "operations",
                "status": "SUCCESS",
                "is_alerting": is_alerting,
                "system_health": health,
                "failure_metrics": failures
            }
        except Exception as e:
            logger.error(f"LanguageDashboardService | Failed to generate operations dashboard: {e}")
            return {
                "generated_at": self._get_timestamp(),
                "dashboard_type": "operations",
                "status": "ERROR", 
                "error": str(e)
            }

    def get_executive_dashboard(self, days: int = 30) -> Dict[str, Any]:
        """
        Responsibility 3: High-Level Executive View
        Strips away distributions and granular failures, providing only top-line KPIs.
        """
        logger.info(f"LanguageDashboardService | Generating executive dashboard payload (days={days})")
        try:
            return {
                "generated_at": self._get_timestamp(),
                "dashboard_type": "executive",
                "status": "SUCCESS",
                "executive_summary": self.metrics_service.get_executive_summary(days=days)
            }
        except Exception as e:
            logger.error(f"LanguageDashboardService | Failed to generate executive dashboard: {e}")
            return {
                "generated_at": self._get_timestamp(),
                "dashboard_type": "executive",
                "status": "ERROR", 
                "error": str(e)
            }