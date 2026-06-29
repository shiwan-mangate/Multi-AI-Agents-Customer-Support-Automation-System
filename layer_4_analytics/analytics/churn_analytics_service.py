# layer_4_analytics/analytics/churn_analytics_service.py

from typing import List, Dict, Any

from layer_4_analytics.schemas.churn_metrics import ChurnMetrics


class ChurnAnalyticsService:
    """
    Predictive business intelligence engine for identifying at-risk customers.
    Analyzes historical health signals, classifies customers into strict schema-compliant 
    Risk Tiers, and generates human-readable risk drivers for Customer Success teams.
    """

    
    LOW_RISK_MAX = 30
    MEDIUM_RISK_MAX = 60

 
    SENTIMENT_THRESHOLD = -0.5
    UNRESOLVED_TICKETS_THRESHOLD = 3
    INACTIVITY_THRESHOLD_DAYS = 30

    @staticmethod
    def calculate_churn_metrics(mapped_rows: List[Dict[str, Any]]) -> List[ChurnMetrics]:
        """
        Processes normalized customer health rows to compute risk classifications 
        and actionable risk drivers.
        """
        results: List[ChurnMetrics] = []

        for row in mapped_rows:
         
            risk_score = row.get("risk_score", 0.0)
            sentiment_score = row.get("sentiment_score", 0.0)
            unresolved_tickets = row.get("unresolved_tickets", 0)
            days_inactive = row.get("days_inactive", 0)

        
            if risk_score <= ChurnAnalyticsService.LOW_RISK_MAX:
                risk_level = "low"
            elif risk_score <= ChurnAnalyticsService.MEDIUM_RISK_MAX:
                risk_level = "medium"
            else:
                risk_level = "high"

        
            risk_drivers: List[str] = []

            if sentiment_score < ChurnAnalyticsService.SENTIMENT_THRESHOLD:
                risk_drivers.append("negative_sentiment")

            if unresolved_tickets >= ChurnAnalyticsService.UNRESOLVED_TICKETS_THRESHOLD:
                risk_drivers.append("unresolved_tickets")

            if days_inactive >= ChurnAnalyticsService.INACTIVITY_THRESHOLD_DAYS:
                risk_drivers.append("customer_inactivity")

            # NEW
            if risk_level != "low" and not risk_drivers:
                if days_inactive >= ChurnAnalyticsService.INACTIVITY_THRESHOLD_DAYS:
                    risk_drivers.append("customer_inactivity")
                elif unresolved_tickets > 0:
                    risk_drivers.append("unresolved_tickets")
                elif sentiment_score < 0:
                    risk_drivers.append("negative_sentiment")
                else:
                    # Fallback so the schema remains valid
                    risk_drivers.append("declining_usage")

           
            metrics = ChurnMetrics(
                customer_id=row.get("customer_id"),
                customer_name=row.get("customer_name", "Unknown Customer"),
                risk_score=round(risk_score, 2),
                risk_level=risk_level,
                risk_drivers=risk_drivers,
                last_sentiment_score=round(sentiment_score, 2),
                unresolved_ticket_count=unresolved_tickets,
                days_since_last_activity=days_inactive
            )
            
            results.append(metrics)

        return results