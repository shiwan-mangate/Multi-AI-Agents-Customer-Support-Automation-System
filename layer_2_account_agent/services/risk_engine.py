import logging
from typing import Dict, Any, Optional

from layer_2_account_agent.schemas.domain import (
    RiskLevel,
    RiskAssessment,
    ActionType,
    AbuseAssessment,
    TakeoverAssessment
)

logger = logging.getLogger(__name__)

class RiskEngineService:
    """
    Central unified security/business risk engine.
    Combines:
    - abuse risk
    - takeover risk
    - business context risk
    """
    HIGH_RISK_THRESHOLD = 75.0
    MEDIUM_RISK_THRESHOLD = 40.0
    HIGH_VALUE_LTV_THRESHOLD = 1000.0

    HIGH_SENSITIVITY_ACTIONS = {
        ActionType.SUBSCRIPTION_CANCEL,
        ActionType.PAYMENT_UPDATE_LINK,
        ActionType.SUBSCRIPTION_DOWNGRADE,
        ActionType.ACCESS_SYNC
    }

    def calculate_risk(
        self,
        triage_context: Dict[str, Any],
        requested_action: Optional[ActionType],
        abuse_assessment: AbuseAssessment,
        takeover_assessment: TakeoverAssessment
    ) -> RiskAssessment:
        
        signals: Dict[str, Any] = {}
        risk_score = 0.0

        if takeover_assessment.takeover_detected:
            signals["takeover_detected"] = True
            risk_score += 75.0
        else:
            risk_score += takeover_assessment.risk_score_modifier

        signals.update({
            f"ato_{k}": v
            for k, v in takeover_assessment.signals.items()
        })

        if abuse_assessment.abuse_detected:
            signals["abuse_detected"] = True
            risk_score += 50.0
        else:
            risk_score += (abuse_assessment.abuse_score * 0.5)

        signals.update({
            f"abuse_{k}": v
            for k, v in abuse_assessment.signals.items()
        })

        total_tickets = int(
            triage_context.get("total_tickets") or 0
        )

        unresolved_repeat_count = int(
            triage_context.get("unresolved_repeat_count") or 0
        )

        ltv = float(
            triage_context.get("ltv") or 0.0
        )

        # FIX: Safe casting to string to prevent NoneType evaluation drifts against schema Enums
        customer_tier = str(triage_context.get(
            "customer_tier",
            "standard"
        ) or "standard").lower()

        # New / unknown account
        if total_tickets == 0 and ltv == 0.0:
            signals["zero_history_account"] = True
            risk_score += 15.0

        # Repeated unresolved operational behavior
        if unresolved_repeat_count >= 2:
            signals["repeat_operational_behavior"] = True
            risk_score += 10.0

        # High-value sensitive operation
        if (
            requested_action is not None
            and requested_action in self.HIGH_SENSITIVITY_ACTIONS
            and ltv >= self.HIGH_VALUE_LTV_THRESHOLD
        ):
            signals["high_value_sensitive_action"] = True
            risk_score += 15.0

        # VIP / enterprise protection uplift
        if (
            customer_tier in {"premium", "enterprise"}
            and requested_action in self.HIGH_SENSITIVITY_ACTIONS
        ):
            signals["high_tier_protection"] = True
            risk_score += 10.0

        final_score = max(0.0, min(100.0, risk_score))

        if final_score >= self.HIGH_RISK_THRESHOLD:
            risk_level = RiskLevel.HIGH
        elif final_score >= self.MEDIUM_RISK_THRESHOLD:
            risk_level = RiskLevel.MEDIUM
        else:
            risk_level = RiskLevel.LOW

        assessment = RiskAssessment(
            risk_score=final_score,
            risk_level=risk_level,
            takeover_detected=takeover_assessment.takeover_detected,
            abuse_detected=abuse_assessment.abuse_detected,
            signals=signals
        )

        logger.info(
            "Risk calculated action=%s score=%s level=%s",
            requested_action.value if requested_action else "none",
            final_score,
            risk_level.value
        )

        return assessment