# layer_4_analytics/analytics/satisfaction_analytics_service.py

from datetime import datetime
from typing import List, Dict, Any

from layer_4_analytics.schemas.satisfaction_metrics import SatisfactionMetrics


class SatisfactionAnalyticsService:
    """
    Core business intelligence engine for computing top-level Customer Satisfaction (CSAT).
    Analyzes historical trends, feedback distributions, and net satisfaction percentages.
    """

    @staticmethod
    def _calculate_distribution_and_rate(rows: List[Dict[str, Any]]) -> tuple[int, int, int, int, float]:
        """
        Internal helper to safely compute distribution buckets and the overall 
        satisfaction rate while ignoring 'unknown' or corrupted mapping labels.
        """
        positive_count = sum(1 for r in rows if r.get("feedback_type") == "positive")
        negative_count = sum(1 for r in rows if r.get("feedback_type") == "negative")
        neutral_count  = sum(1 for r in rows if r.get("feedback_type") == "neutral")

        total_count = positive_count + negative_count + neutral_count

        satisfaction_rate = 0.0
        if total_count > 0:
            satisfaction_rate = (positive_count / total_count) * 100.0

        return positive_count, negative_count, neutral_count, total_count, satisfaction_rate

    @staticmethod
    def calculate_satisfaction_metrics(
        current_rows: List[Dict[str, Any]],
        previous_rows: List[Dict[str, Any]],
        period_start: datetime,
        period_end: datetime
    ) -> SatisfactionMetrics:
        """
        Computes CSAT distributions and period-over-period trend velocity.
        """
  
        pos, neg, neu, total, current_rate = SatisfactionAnalyticsService._calculate_distribution_and_rate(current_rows)

   
        _, _, _, _, previous_rate = SatisfactionAnalyticsService._calculate_distribution_and_rate(previous_rows)

  
        trend_percentage = current_rate - previous_rate

    
        return SatisfactionMetrics(
            positive_feedback_count=pos,
            negative_feedback_count=neg,
            neutral_feedback_count=neu,
            total_feedback_count=total,
            satisfaction_rate=round(current_rate, 2),
            previous_period_rate=round(previous_rate, 2),
            trend_percentage=round(trend_percentage, 2),
            period_start=period_start,
            period_end=period_end
        )