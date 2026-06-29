# layer_4_analytics/services/churn_monitor_service.py

from typing import List, Dict
from layer_4_analytics.schemas.churn_metrics import ChurnMetrics


class ChurnMonitorService:
    """
    Action engine for Customer Success teams.
    Consumes pre-calculated ChurnMetrics and filters, sorts, and aggregates them 
    to surface immediately actionable insights and dashboard alerts.
    """

    
    DEFAULT_HIGH_RISK_THRESHOLD = 61.0

    @staticmethod
    def get_high_risk_customers(
        metrics: List[ChurnMetrics], 
        risk_threshold: float = DEFAULT_HIGH_RISK_THRESHOLD
    ) -> List[ChurnMetrics]:
        """
        Filters and sorts the customer base to return only those requiring immediate intervention.
        Sorted from highest risk to lowest risk.
        """
        at_risk = [m for m in metrics if m.risk_score >= risk_threshold]
        
        
        return sorted(at_risk, key=lambda x: x.risk_score, reverse=True)

    @staticmethod
    def get_top_n_risks(metrics: List[ChurnMetrics], limit: int = 10) -> List[ChurnMetrics]:
        """
        Returns the absolute top 'N' highest risk customers, regardless of threshold.
        Useful for executive "Top 10 Fires" reports.
        """
        sorted_metrics = sorted(metrics, key=lambda x: x.risk_score, reverse=True)
        return sorted_metrics[:limit]

    @staticmethod
    def summarize_risk_distribution(metrics: List[ChurnMetrics]) -> Dict[str, int]:
        """
        Aggregates the customer base into a high-level distribution summary.
        Perfect for rendering a pie chart or summary widget on the Dashboard UI.
        """
        distribution = {
            "low": 0,
            "medium": 0,
            "high": 0
        }

        for metric in metrics:
            if metric.risk_level in distribution:
                distribution[metric.risk_level] += 1

        return distribution