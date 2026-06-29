from typing import Dict, Any, List

class ScoringEngine:
    """
    Deterministic brain for calculating priority scores.
    Refined for LTV nuance and operational safety (Decoupled Confidence).
    """

    @staticmethod
    def calculate_urgency_score(urgency: str) -> float:
        mapping = {
            "low": 2.0,
            "medium": 5.0,
            "high": 8.0,
            "urgent": 10.0  # FIX: Aligned with tickets.priority Schema ("critical" removed)
        }
        return mapping.get(urgency.lower(), 5.0)

    @staticmethod
    def calculate_ltv_score(tier: str, ltv: float) -> float:
        """
        Calculates LTV score with a smooth additive bump to maintain nuance.
        Standard ($0) -> 2.0 | Premium ($50k) -> 7.5 | Enterprise ($50k) -> 10.0
        """
        # FIX: Aligned with customers.account_tier Schema ("vip" removed)
        tier_scores = {"standard": 2.0, "premium": 6.0, "enterprise": 9.0} 
        base = tier_scores.get(tier.lower() if tier else "standard", 2.0)
        spending_bonus = min(ltv / 50000, 1.0) * 1.5
        return min(base + spending_bonus, 10.0)

    @staticmethod
    def calculate_sentiment_score(current: str, last: str) -> float:
        # FIX: Aligned with tickets.sentiment Schema ("calm" changed to "positive")
        sentiment_map = {"positive": 1.0, "neutral": 3.0, "frustrated": 7.0, "angry": 10.0}
        curr_val = sentiment_map.get(current.lower(), 5.0)
        last_val = sentiment_map.get(last.lower() if last else "neutral", 3.0)
        if curr_val > last_val:
            return min(curr_val + 1.5, 10.0)
        return curr_val
    
    @staticmethod
    def calculate_history_score(repeats: int, escalations: int, tags: List[str]) -> float:
        """
        Calculates score based on failure loops. 
        Note: Watch for saturation with multiple previous escalations.
        """
        score = (repeats * 2.0) + (escalations * 3.0)
        
        if "customer_contact_spike" in tags:
            score += 2.0
            
        return min(score, 10.0)

    @classmethod
    def get_full_scorecard(cls, state_data: Dict[str, Any]) -> Dict[str, float]:
        """
        Executes the deterministic formula:
        $$P = (U \cdot 0.4) + (L \cdot 0.3) + (S \cdot 0.2) + (H \cdot 0.1)$$
        """
        u = cls.calculate_urgency_score(state_data.get("initial_urgency", "medium"))
        l = cls.calculate_ltv_score(state_data.get("customer_tier", "standard"), state_data.get("ltv", 0.0))
        s = cls.calculate_sentiment_score(state_data.get("initial_sentiment", "neutral"), state_data.get("last_sentiment"))
        h = cls.calculate_history_score(
            state_data.get("unresolved_repeat_count", 0),
            state_data.get("total_escalations", 0),
            state_data.get("insight_tags", [])
        )

        final = (u * 0.4) + (l * 0.3) + (s * 0.2) + (h * 0.1)

        return {
            "urgency_score": round(u, 2),
            "ltv_score": round(l, 2),
            "sentiment_score": round(s, 2),
            "history_score": round(h, 2),
            "final_score": round(final, 2) 
        }