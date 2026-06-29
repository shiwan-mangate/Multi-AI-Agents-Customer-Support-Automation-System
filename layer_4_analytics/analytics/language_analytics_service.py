# layer_4_analytics/analytics/language_analytics_service.py

from datetime import datetime
from typing import List, Dict, Any, Set

from layer_4_analytics.schemas.language_metrics import LanguageMetrics


class LanguageAnalyticsService:
    """
    Core business intelligence engine for computing Layer 3 Translation Health.
    Calculates language adoption, translation reliability, and period-over-period 
    market growth strictly for supported translation models.
    """

    CANONICAL_LANGUAGE_NAMES = {
        "en": "English",
        "hi": "Hindi",
        "es": "Spanish",
        "fr": "French",
        "de": "German",
        "ar": "Arabic"
    }

    @staticmethod
    def calculate_language_metrics(
        current_rows: List[Dict[str, Any]],
        previous_rows: List[Dict[str, Any]],
        period_start: datetime,
        period_end: datetime,
        satisfaction_lookup: Dict[str, float] = None
    ) -> List[LanguageMetrics]:
        """
        Groups translation events by language, computes success ratios,
        and constructs the final reporting schemas.
        """
        if satisfaction_lookup is None:
            satisfaction_lookup = {}

        unique_current = {}
        for row in current_rows:
            key = (
                row.get("ticket_id"),
                row.get("language_code"),
            )
            if key not in unique_current:
                unique_current[key] = row
        current_rows = list(unique_current.values())

        print("=" * 60)
        print("Before dedup :", len(unique_current))
        print("After dedup  :", len(current_rows))
        print("English rows :", sum(1 for r in current_rows if r["language_code"] == "en"))
        print("=" * 60)

        current_stats: Dict[str, Dict[str, int]] = {}
        for row in current_rows:
            code = row.get("language_code", "unknown")
            
            if code == "unknown":
                continue
                
            if code not in current_stats:
                current_stats[code] = {"total": 0, "success": 0}
                
            current_stats[code]["total"] += 1
            if row.get("translation_success") is True:
                current_stats[code]["success"] += 1

        unique_previous = {}
        for row in previous_rows:
            key = (
                row.get("ticket_id"),
                row.get("language_code"),
            )
            if key not in unique_previous:
                unique_previous[key] = row
        previous_rows = list(unique_previous.values())

        previous_counts: Dict[str, int] = {}
        for row in previous_rows:
            code = row.get("language_code", "unknown")
            if code == "unknown":
                continue
            previous_counts[code] = previous_counts.get(code, 0) + 1

        all_languages: Set[str] = set(current_stats.keys()).union(set(previous_counts.keys()))

        results: List[LanguageMetrics] = []

        for lang_code in sorted(all_languages):
            
            if lang_code not in LanguageAnalyticsService.CANONICAL_LANGUAGE_NAMES:
                continue

            lang_name = LanguageAnalyticsService.CANONICAL_LANGUAGE_NAMES[lang_code]

            stats = current_stats.get(lang_code, {"total": 0, "success": 0})
            current_count = stats["total"]
            success_count = stats["success"]

            success_rate = 0.0
            if current_count > 0:
                success_rate = (success_count / current_count) * 100.0

            prev_count = previous_counts.get(lang_code, 0)
            if prev_count == 0:
                growth_rate = None
            else:
                raw_growth = ((current_count - prev_count) / prev_count) * 100.0
                growth_rate = round(raw_growth, 2)

            satisfaction_rate = satisfaction_lookup.get(lang_code, 0.0)

            metrics = LanguageMetrics(
                language_code=lang_code,
                language_name=lang_name,
                ticket_count=current_count,
                satisfaction_rate=round(satisfaction_rate, 2),
                translation_success_rate=round(success_rate, 2),
                previous_period_count=prev_count,
                growth_rate=growth_rate,
                period_start=period_start,
                period_end=period_end
            )
            
            results.append(metrics)

        return results