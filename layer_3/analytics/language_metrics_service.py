import logging
from typing import Dict, Any, Optional
from layer_3.storage.translation_analytics_service import TranslationAnalyticsService
logger = logging.getLogger(__name__)

class LanguageMetricsService:
    """
    Operational Metrics Engine for Layer 3.
    Transforms raw repository analytics into Business KPIs for BI and Dashboards.
    """

    # TODO: Phase 2 - Move these to config/translation_settings.py
    HEALTHY_THRESHOLD = 98.0
    WARNING_THRESHOLD = 95.0

    def __init__(self, analytics_service: TranslationAnalyticsService):
        # Injected TranslationAnalyticsService. No direct DB awareness.
        self.analytics_service = analytics_service

    def get_system_health_metrics(self) -> Dict[str, Any]:
        """
        Responsibility 1: System Health Metrics
        Calculates success/failure rates and classifies overall health.
        """
        try:
            raw_data = self.analytics_service.get_translation_health_metrics()
            
            total = raw_data.get("total", 0)
            success = raw_data.get("success", 0)
            failed = raw_data.get("failed", 0)
            success_rate = raw_data.get("success_rate", 0.0)

            # Calculate failure rate explicitly
            failure_rate = round(100.0 - success_rate, 2) if total > 0 else 0.0

            # Health Classification Logic
            if total == 0:
                health_status = "UNKNOWN"
            elif success_rate >= self.HEALTHY_THRESHOLD:
                health_status = "HEALTHY"
            elif success_rate >= self.WARNING_THRESHOLD:
                health_status = "WARNING"
            else:
                health_status = "URGENT"

            return {
                "total_translations": total,
                "successful_translations": success,
                "failed_translations": failed,
                "success_rate": success_rate,
                "failure_rate": failure_rate,
                "system_health": health_status
            }
        except Exception as e:
            logger.error(f"LanguageMetricsService | Failed to calculate system health: {e}")
            return {
                "system_health": "ERROR", 
                "error": str(e)
            }

    def get_language_usage_metrics(self, days: int = 30) -> Dict[str, Any]:
        """
        Responsibility 2: Language Usage Metrics
        Extracts active language counts and top language parameters.
        """
        try:
            distribution = self.analytics_service.get_language_distribution(days)
            
            active_languages = len(distribution)
            top_language = None
            top_language_percentage = 0.0

            if active_languages > 0:
                # Find the language with the highest count
                top_lang_key = max(distribution, key=lambda k: distribution[k].get("count", 0))
                top_language = top_lang_key
                top_language_percentage = distribution[top_lang_key].get("percentage", 0.0)

            return {
                "active_languages": active_languages,
                "top_language": top_language,
                "top_language_percentage": top_language_percentage,
                "distribution": distribution
            }
        except Exception as e:
            logger.error(f"LanguageMetricsService | Failed to calculate usage metrics: {e}")
            return {
                "active_languages": 0, 
                "distribution": {}, 
                "error": str(e)
            }

    def get_failure_metrics(self, limit: int = 100) -> Dict[str, Any]:
        """
        Responsibility 3: Failure Metrics
        Identifies the most problematic languages for rapid triage.
        """
        try:
            report = self.analytics_service.get_failed_translation_report(limit)
            
            failure_count = report.get("failure_count", 0)
            breakdown = report.get("failure_by_language", {})
            
            affected_languages = len(breakdown)
            most_problematic = None

            if affected_languages > 0:
                most_problematic = max(breakdown, key=breakdown.get)

            return {
                "failure_count": failure_count,
                "affected_languages": affected_languages,
                "most_problematic_language": most_problematic,
                "failure_breakdown": breakdown
            }
        except Exception as e:
            logger.error(f"LanguageMetricsService | Failed to calculate failure metrics: {e}")
            return {
                "failure_count": 0, 
                "affected_languages": 0, 
                "error": str(e)
            }

    def get_customer_adoption_metrics(self, customer_id: int) -> Dict[str, Any]:
        """
        Responsibility 4: Customer Language Adoption Metrics
        Determines customer language dominance and multi-lingual status.
        """
        try:
            profile = self.analytics_service.get_customer_language_profile(customer_id)
            if not profile:
                return {"multilingual_customer": False, "translation_count": 0}

            preferred_language = profile.get("preferred_language")
            history = profile.get("language_history", [])
            total = profile.get("total_translations", 0)
            dominance = profile.get("dominance_score", 0.0)

            # Business Logic: Is this customer polyglot?
            is_multilingual = len(set(history)) > 1

            return {
                "preferred_language": preferred_language,
                "dominance_score": dominance,
                "multilingual_customer": is_multilingual,
                "translation_count": total
            }
        except Exception as e:
            logger.error(f"LanguageMetricsService | Failed to calculate adoption for CustomerID={customer_id}: {e}")
            return {
                "multilingual_customer": False, 
                "translation_count": 0, 
                "error": str(e)
            }

    def get_executive_summary(self, days: int = 30) -> Dict[str, Any]:
        """
        Responsibility 5: Executive Summary
        Aggregates health, usage, and failure metrics into a single high-level DTO.
        """
        try:
            health = self.get_system_health_metrics()
            
            # If health failed, don't cascade the failure, just report it
            if "error" in health:
                return {"system_health": "ERROR", "error": health["error"]}

            usage = self.get_language_usage_metrics(days)
            failures = self.get_failure_metrics()

            return {
                "total_translations": health.get("total_translations", 0),
                "success_rate": health.get("success_rate", 0.0),
                "failure_rate": health.get("failure_rate", 0.0),
                "system_health": health.get("system_health", "UNKNOWN"),
                "failed_translations": health.get("failed_translations", 0),
                "top_language": usage.get("top_language"),
                "active_languages": usage.get("active_languages", 0),
                "translation_growth": "NOT_IMPLEMENTED" # TODO: Phase 2 date-based grouping
            }
        except Exception as e:
            logger.critical(f"LanguageMetricsService | Failed to generate executive summary: {e}")
            return {
                "system_health": "ERROR", 
                "error": str(e)
            }