import logging
from typing import List, Optional

from layer_2_escalation_agent.schemas.risk_assessment import RiskAssessment, RiskLevel
from layer_2_escalation_agent.schemas.trigger_assessment import TriggerAssessment
from layer_2_escalation_agent.schemas.customer_context import CustomerContext

logger = logging.getLogger(__name__)


class RiskEngine:
    """
    Deterministic enterprise escalation severity engine.

    Responsibilities:
    - weighted risk scoring
    - severity classification
    - downstream routing flags
    """

    TRIGGER_WEIGHTS = {
        "legal": 55.0,
        "security": 60.0,
        "sla": 35.0,
        "manual_review": 30.0,
        "churn": 25.0,
        "operational": 20.0,
        "repeat_issue": 20.0,
        "knowledge_gap": 10.0,
        "general": 5.0,
    }

    TIER_WEIGHTS = {
        "enterprise": 20.0,
        "premium": 12.0,
        "standard": 0.0, 
    }

    CRITICAL_OVERRIDE_CATEGORIES = {
        "security",
    }

    def assess(
        self,
        trigger_assessment: TriggerAssessment,
        customer_context: CustomerContext,
        repeat_issue_count: int = 0,
        current_sentiment: str = "neutral",
        sla_breached: bool = False,
        billing_flags: Optional[List[str]] = None,
    ) -> RiskAssessment:
        """
        Calculate deterministic escalation severity.
        """
        billing_flags = billing_flags or []

        category = trigger_assessment.category.value if hasattr(trigger_assessment.category, "value") else str(trigger_assessment.category)

        s_trigger = self._score_trigger(category)
        s_tier = self._score_customer_tier(customer_context.customer_tier)
        s_ltv = self._score_ltv(customer_context.ltv)
        
        s_history = self._score_escalation_history(
            open_count=getattr(customer_context, "open_escalations", 0),
            resolved_count=getattr(customer_context, "resolved_escalations", 0)
        )
        
        s_repeat = self._score_repeat_issues(repeat_issue_count)
        
        s_sentiment = self._score_sentiment(
            current_sentiment=current_sentiment,
            historical_sentiment=getattr(customer_context, "historical_sentiment_trend", "neutral")
        )
        
        s_sla = self._score_sla(sla_breached)
        s_billing = self._score_billing_risk(billing_flags)

        s_feedback = self._score_negative_feedback(
            getattr(customer_context, "negative_feedback_count", 0)
        )
        s_unresolved = self._score_unresolved_tickets(
            getattr(customer_context, "unresolved_ticket_count", 0)
        )
        s_subscription = self._score_subscription_risk(
            getattr(customer_context, "subscription_status", "active")
        )
        s_churn = self._score_churn_score(
            getattr(customer_context, "churn_score", 0.0)
        )

        logger.warning(
        "RISK BREAKDOWN | trigger=%s tier=%s ltv=%s repeat=%s "
        "history=%s sentiment=%s churn=%s subscription=%s",
        s_trigger,
        s_tier,
        s_ltv,
        s_repeat,
        s_history,
        s_sentiment,
        s_churn,
        s_subscription,
    )

        # Add new risk signals to the raw score total
        raw_score = sum([
            s_trigger,
            s_tier,
            s_ltv,
            s_history,
            s_repeat,
            s_sentiment,
            s_sla,
            s_billing,
            s_feedback,      
            s_unresolved,    
            s_subscription,   
            s_churn          
        ])

        final_score = min(max(raw_score, 0.0), 100.0)

        fraud_detected = s_billing > 0

        high_churn_signals = (
            s_sentiment >= 6.0
            and repeat_issue_count >= 2
            and customer_context.ltv > 1000
        )

        critical_override = self._critical_override(
            category=category,
            trigger_assessment=trigger_assessment,
            customer_context=customer_context,
            repeat_issue_count=repeat_issue_count,
            current_sentiment=current_sentiment,
            sla_breached=sla_breached,
            fraud_detected=fraud_detected,
        )

        if critical_override:
            level = RiskLevel.URGENT.value
            final_score = max(final_score, 90.0)
        else:
            level = self._resolve_level(final_score)

        flags = self._build_flags(
            category=category,
            fraud_detected=fraud_detected,
            high_churn_signals=high_churn_signals,
            sla_breached=sla_breached,
        )

        logger.info(
            "Risk assessment complete | raw_score=%.1f | final_score=%.1f | level=%s",
            raw_score,
            final_score,
            level,
        )

        return RiskAssessment(
            score=final_score,
            level=level,
            legal_risk=flags["legal_risk"],
            security_risk=flags["security_risk"],
            churn_risk=flags["churn_risk"],
            sla_risk=flags["sla_risk"],
        )

    def _critical_override(
        self,
        category: str,
        trigger_assessment: TriggerAssessment,
        customer_context: CustomerContext,
        repeat_issue_count: int,
        current_sentiment: str,
        sla_breached: bool,
        fraud_detected: bool,
    ) -> bool:
        """
        Enterprise hard escalation overrides.
        """
        normalized = (category or "").strip().lower()

        reasons = {
            reason.value.lower()
            if hasattr(reason, "value")
            else str(reason).lower()
            for reason in trigger_assessment.reasons
        }

        if normalized == "security":
            return True

        if normalized == "legal" and "takeover_suspicion" in reasons:
            return True

        if normalized == "legal" and fraud_detected:
            return True

        if normalized == "legal" and sla_breached:
            return True

        if (
            normalized == "legal"
            and current_sentiment.lower() == "angry"
            and float(customer_context.ltv) > 1000
        ):
            return True

        if normalized == "legal" and repeat_issue_count >= 2:
            return True

        return False

    def _score_trigger(self, category: str) -> float:
        normalized = (category or "general").strip().lower()
        return self.TRIGGER_WEIGHTS.get(normalized, 5.0)

    def _score_customer_tier(self, tier) -> float:
        if hasattr(tier, "value"):
            normalized = tier.value.lower()
        else:
            normalized = str(tier or "standard").strip().lower()

        return self.TIER_WEIGHTS.get(normalized, 0.0)

    def _score_ltv(self, ltv: float) -> float:
        try:
            value = float(ltv)
            if value > 50000:
                return 20.0
            elif value > 10000:
                return 10.0
            elif value > 1000:
                return 5.0
        except:
            pass
        return 0.0

    def _score_escalation_history(self, open_count: int, resolved_count: int) -> float:
        score = 0.0
        try:
            active = int(open_count)
            resolved = int(resolved_count)

            if active >= 2:
                score += 20.0
            elif active == 1:
                score += 10.0

            if resolved >= 3:
                score += 5.0
                
            return min(score, 25.0)
        except:
            pass
        return 0.0

    def _score_repeat_issues(self, count: int) -> float:
        try:
            repeats = int(count)
            if repeats >= 3:
                return 15.0
            elif repeats >= 2:
                return 8.0
        except:
            pass
        return 0.0

    def _score_sentiment(self, current_sentiment: str, historical_sentiment: str) -> float:
        score = 0.0
        
        # Current Sentiment
        normalized_current = (current_sentiment or "neutral").strip().lower()
        if normalized_current == "angry":
            score += 10.0
        elif normalized_current == "frustrated":
            score += 6.0
            
        # Historical Sentiment
        normalized_historical = (historical_sentiment or "neutral").strip().lower()
        if hasattr(normalized_historical, "value"):
            normalized_historical = normalized_historical.value.lower()
            
        if normalized_historical == "angry":
            score += 10.0
        elif normalized_historical == "frustrated":
            score += 4.0
            
        return score

    def _score_billing_risk(self, billing_flags: List[str]) -> float:
        normalized_flags = {
            str(flag).strip().lower()
            for flag in billing_flags
        }

        if "chargeback" in normalized_flags:
            return 25.0

        if "fraud" in normalized_flags:
            return 25.0

        return 0.0

    def _score_sla(self, breached: bool) -> float:
        return 20.0 if breached else 0.0

    def _score_negative_feedback(self, count: int) -> float:
        if count >= 5:
            return 15.0
        if count >= 2:
            return 8.0
        return 0.0

    def _score_unresolved_tickets(self, count: int) -> float:
        if count >= 5:
            return 20.0
        if count >= 2:
            return 10.0
        return 0.0

    def _score_subscription_risk(self, status: str) -> float:
        normalized = (status or "").lower()
        if normalized == "past_due":
            return 20.0
        if normalized == "suspended":
            return 25.0
        return 0.0

    def _score_churn_score(self, churn_score: float) -> float:
        try:
            score = float(churn_score)
            if score >= 80:
                return 25.0
            if score >= 60:
                return 15.0
            if score >= 40:
                return 8.0
        except:
            pass
        return 0.0

    # 🟢 FIX 5 Reverted: Restored original production distribution thresholds
    def _resolve_level(self, score: float) -> str:
        if score >= 80:
            return RiskLevel.URGENT.value

        if score >= 50:
            return RiskLevel.HIGH.value

        if score >= 20:
            return RiskLevel.MEDIUM.value

        return RiskLevel.LOW.value

    def _build_flags(
        self,
        category: str,
        fraud_detected: bool,
        high_churn_signals: bool,
        sla_breached: bool,
    ):
        normalized = (category or "").strip().lower()

        return {
            "legal_risk": normalized == "legal",
            "security_risk": normalized == "security" or fraud_detected,
            "churn_risk": normalized == "churn" or high_churn_signals,
            "sla_risk": normalized == "sla" or sla_breached,
        }