import logging
from typing import Dict, Any, Optional
from datetime import datetime, UTC

from layer_2_account_agent.schemas.domain import (
    ActionType,
    TakeoverAssessment
)

logger = logging.getLogger(__name__)


class TakeoverDetectorService:
    """
    Deterministic account takeover detection engine.

    Detects:
    - suspicious flagged accounts
    - post-password-reset velocity attacks
    - locked MFA bypass attempts
    - high-risk operational abuse
    """

    RECENT_RESET_WINDOW_HOURS = 24
    TAKEOVER_THRESHOLD = 75.0

    HIGH_RISK_ACTIONS = {
        ActionType.SUBSCRIPTION_UPGRADE,
        ActionType.SUBSCRIPTION_DOWNGRADE,
        ActionType.SUBSCRIPTION_CANCEL,
        ActionType.PAYMENT_UPDATE_LINK,
        ActionType.ACCESS_SYNC,
    }

    def evaluate_takeover_risk(
        self,
        auth_context: Optional[Dict[str, Any]],
        requested_action: Optional[ActionType]
    ) -> TakeoverAssessment:
        """
        Evaluate account takeover risk patterns.
        """

        if not auth_context:
            return TakeoverAssessment(
                takeover_detected=False,
                risk_score_modifier=0.0,
                signals={},
                reason="No authentication context available"
            )

        signals: Dict[str, Any] = {}
        reasons = []
        takeover_score = 0.0

        now = datetime.now(UTC)

        suspicious_flag = bool(
            auth_context.get("suspicious_flag", False)
        )

        mfa_enabled = bool(
            auth_context.get("two_factor_enabled", False)
        )

        account_locked = bool(
            auth_context.get("account_locked", False)
        )

        last_reset_dt = auth_context.get("last_password_reset_at")
        normalized_reset_dt = self._normalize_datetime(last_reset_dt)



        if suspicious_flag:
            signals["suspicious_flag_active"] = True
            takeover_score += 35.0
            reasons.append("Account previously flagged suspicious")



        if normalized_reset_dt:
            hours_since_reset = (
                (now - normalized_reset_dt).total_seconds() / 3600.0
            )

            if hours_since_reset <= self.RECENT_RESET_WINDOW_HOURS:
                signals["recent_password_reset_hours"] = round(
                    hours_since_reset,
                    1
                )

                if (
                    requested_action is not None
                    and requested_action in self.HIGH_RISK_ACTIONS
                ):
                    signals["velocity_attack_detected"] = True
                    takeover_score += 65.0

                    reasons.append(
                        f"High-risk action after recent password reset "
                        f"({hours_since_reset:.1f}h)"
                    )
                else:
                    takeover_score += 15.0
                    reasons.append(
                        f"Recent password reset ({hours_since_reset:.1f}h)"
                    )



        if (
            account_locked
            and mfa_enabled
            and requested_action is not None
            and requested_action != ActionType.PASSWORD_RESET
        ):
            signals["locked_mfa_bypass_attempt"] = True
            takeover_score += 55.0

            reasons.append(
                "Operational request against locked MFA-protected account"
            )



        if (
            account_locked
            and requested_action in self.HIGH_RISK_ACTIONS
        ):
            signals["locked_high_risk_action"] = True
            takeover_score += 25.0

            reasons.append(
                "High-risk action requested from locked account"
            )



        takeover_score = max(0.0, min(100.0, takeover_score))

        takeover_detected = (
            takeover_score >= self.TAKEOVER_THRESHOLD
        )

        final_reason = (
            " | ".join(reasons)
            if reasons
            else "No takeover indicators detected"
        )

        if takeover_detected:
            logger.warning(
                "Account takeover risk detected score=%s reason=%s",
                takeover_score,
                final_reason
            )

        return TakeoverAssessment(
            takeover_detected=takeover_detected,
            risk_score_modifier=takeover_score,
            signals=signals,
            reason=final_reason
        )

    def _normalize_datetime(
        self,
        dt: Optional[datetime]
    ) -> Optional[datetime]:
        """
        Normalize database timestamps to UTC-aware datetime.
        """

        if not dt:
            return None

        if dt.tzinfo is None:
            return dt.replace(tzinfo=UTC)

        return dt