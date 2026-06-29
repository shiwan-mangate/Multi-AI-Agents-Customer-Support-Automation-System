# layer_4_analytics/analytics/intent_analytics_service.py

from datetime import datetime
from typing import List, Dict, Any, Set

from layer_4_analytics.schemas.intent_metrics import IntentMetrics


class IntentAnalyticsService:
    """
    Core business intelligence engine for computing Layer 1 routing traffic.
    Calculates exact traffic volumes, proportional distributions, and 
    period-over-period growth trajectories for every intent category.
    """

    KNOWN_INTENTS = {
        "faq", 
        "refund_request", 
        "account_issue", 
        "technical_bug", 
        "angry_complex"
    }

    @staticmethod
    def calculate_intent_metrics(
        current_rows: List[Dict[str, Any]],
        previous_rows: List[Dict[str, Any]],
        period_start: datetime,
        period_end: datetime
    ) -> List[IntentMetrics]:
        """
        Groups transcript events by intent_name, calculates baseline growth,
        and constructs the final reporting schemas.
        """
        total_current_tickets = len(current_rows)

        
        current_counts: Dict[str, int] = {}
        for row in current_rows:
            intent = row.get("intent_name", "unclassified")
            current_counts[intent] = current_counts.get(intent, 0) + 1

        previous_counts: Dict[str, int] = {}
        for row in previous_rows:
            intent = row.get("intent_name", "unclassified")
            previous_counts[intent] = previous_counts.get(intent, 0) + 1

        
        all_intents: Set[str] = set(current_counts.keys()).union(set(previous_counts.keys()))

        results: List[IntentMetrics] = []

       
        for intent_name in sorted(all_intents):
            current_count = current_counts.get(intent_name, 0)
            prev_count = previous_counts.get(intent_name, 0)

            
            percentage = 0.0
            if total_current_tickets > 0:
                percentage = (current_count / total_current_tickets) * 100.0

            
            if prev_count == 0:
                growth_rate = None
            else:
                raw_growth = ((current_count - prev_count) / prev_count) * 100.0
                growth_rate = round(raw_growth, 2)

           
            metrics = IntentMetrics(
                intent_name=intent_name,
                ticket_count=current_count,
                percentage=round(percentage, 2),
                previous_period_count=prev_count,
                growth_rate=growth_rate,
                period_start=period_start,
                period_end=period_end
            )
            
            results.append(metrics)

        return results