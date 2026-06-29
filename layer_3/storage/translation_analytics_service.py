import logging
from collections import Counter
from typing import Dict, Any

from layer_3.repositories.translation_repository import TranslationRepository

logger = logging.getLogger(__name__)

class TranslationAnalyticsService:
    """
    Transforms raw database translation metrics into business-friendly analytics.
    Enriched with observability logging, dominance scoring, and failure breakdowns.
    """

    def __init__(self, repository: TranslationRepository):
        self.repository = repository

    def get_translation_health_metrics(self) -> Dict[str, Any]:
        """Calculates the overall system translation success rate."""
        metrics = self.repository.get_translation_metrics()
        
        total = metrics.get("total", 0)
        success = metrics.get("success", 0)
        failed = metrics.get("failed", 0)
        
        # Guard against Day-1 Division by Zero
        success_rate = round((success / total * 100), 2) if total > 0 else 0.0

        logger.info(
            f"TranslationAnalyticsService | Health Metrics | "
            f"Total={total} | Success={success} | Failed={failed} | Rate={success_rate}%"
        )

        return {
            "total": total,
            "success": success,
            "failed": failed,
            "success_rate": success_rate
        }

    def get_language_distribution(self, days: int = 30) -> Dict[str, Dict[str, float]]:
        """Enriches raw language usage counts with percentage distributions."""
        usage_counts = self.repository.get_recent_language_usage(days=days)
        total_usage = sum(usage_counts.values())
        
        distribution = {}
        if total_usage > 0:
            for language, count in usage_counts.items():
                distribution[language] = {
                    "count": count,
                    "percentage": round((count / total_usage * 100), 2)
                }

        
        sorted_distribution = dict(sorted(distribution.items(), key=lambda item: item[1]["count"], reverse=True))

        logger.info(
            f"TranslationAnalyticsService | Language Distribution | "
            f"Days={days} | Languages={len(sorted_distribution)} | TotalUsage={total_usage}"
        )

        return sorted_distribution

    def get_customer_language_profile(self, customer_id: int) -> Dict[str, Any]:
        """
        Derives customer language intelligence from their translation history.
        Used to feed the ContextSignalResolver for proactive formatting.
        """
        history_records = self.repository.get_customer_history(customer_id=customer_id)
        
        if not history_records:
            logger.info(
                f"TranslationAnalyticsService | Customer Profile | "
                f"Customer={customer_id} | Preferred=en | Dominance=1.0"
            )
            return {
                "preferred_language": "en",
                "language_history": [],
                "total_translations": 0,
                "dominance_score": 1.0
            }

        languages = [
            record.original_language 
            for record in history_records 
            if getattr(record, 'original_language', None)
        ]
        
        if not languages:
            return {
                "preferred_language": "en",
                "language_history": [],
                "total_translations": len(history_records),
                "dominance_score": 1.0
            }

        counter = Counter(languages)
        preferred_language, count = counter.most_common(1)[0]
        dominance_score = round((count / len(languages)), 2)

        logger.info(
            f"TranslationAnalyticsService | Customer Profile | "
            f"Customer={customer_id} | Preferred={preferred_language} | Dominance={dominance_score}"
        )

        return {
            "preferred_language": preferred_language,
            "language_history": languages,
            "total_translations": len(history_records),
            "dominance_score": dominance_score
        }

    def get_failed_translation_report(self, limit: int = 100) -> Dict[str, Any]:
        """Aggregates and categorizes failed translation records."""
        failed_records = self.repository.get_failed_translations(limit=limit)
        
      
        failure_by_language = dict(Counter(
            getattr(record, 'original_language', 'unknown') 
            for record in failed_records
        ))

        logger.info(
            f"TranslationAnalyticsService | Failed Report | "
            f"Failures={len(failed_records)} | AffectedLanguages={len(failure_by_language)}"
        )

        return {
            "failure_count": len(failed_records),
            "failure_by_language": failure_by_language,
            "records": failed_records
        }