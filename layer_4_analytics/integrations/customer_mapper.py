# layer_4_analytics/integrations/customer_mapper.py
from typing import Dict, List, Any


class CustomerMapper:
    """
    Anti-Corruption Layer (ACL) for Customer metrics.
    Translates raw database rows into clean analytical inputs 
    for the ChurnAnalyticsService. Contains absolutely zero business logic.
    """

    @staticmethod
    def map_customer_row(row: Dict[str, Any]) -> Dict[str, Any]:
        """
        Maps a single raw customer database dictionary into a clean analytics dictionary.
        Renames DB-specific columns to analytic standard names and handles NULLs safely.
        """
   
        raw_id = row.get("customer_id")
        raw_name = row.get("customer_name")
        raw_risk = row.get("churn_risk_score")
        raw_sentiment = row.get("last_sentiment_score")

        if raw_sentiment is None:
            raw_sentiment = "neutral"
        else:
            raw_sentiment = str(raw_sentiment).lower().strip()

        raw_tickets = row.get("unresolved_ticket_count")
        raw_inactive = row.get("days_since_last_activity")
        sentiment_lookup = {
            "happy": 1.0,
            "positive": 1.0,
            "satisfied": 0.8,
            "neutral": 0.0,
            "frustrated": -0.7,
            "angry": -1.0,
        }

        return {
        
            "customer_id": raw_id,
            "customer_name": str(raw_name) if raw_name else "Unknown Customer",
            
          
            "risk_score": float(raw_risk) if raw_risk is not None else 0.0,
            "sentiment_score": sentiment_lookup.get(raw_sentiment, 0.0),
            "unresolved_tickets": int(raw_tickets) if raw_tickets is not None else 0,
            "days_inactive": int(raw_inactive) if raw_inactive is not None else 0
        }

    @classmethod
    def map_customer_rows(cls, rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Bulk maps a list of raw customer database dictionaries.
        """
        return [cls.map_customer_row(row) for row in rows]