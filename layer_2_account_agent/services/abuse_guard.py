import logging
from typing import Dict, Any, Optional

from layer_2_account_agent.schemas.domain import AbuseAssessment

logger = logging.getLogger(__name__)


class AbuseGuardService:
    """
    Deterministic abuse detection engine.

    Detects:
    - brute force authentication abuse
    - ticket spamming
    - escalation abuse
    - suspicious operational behavior
    """



    MAX_SAFE_FAILED_LOGINS = 5
    CRITICAL_FAILED_LOGINS = 8

    MAX_UNRESOLVED_REPEATS = 3

    ESCALATION_ABUSE_MIN_COUNT = 3
    ESCALATION_ABUSE_RATIO = 0.5

    ABUSE_SCORE_THRESHOLD = 75.0

    def evaluate_abuse(
        self,
        auth_context: Optional[Dict[str, Any]],
        triage_context: Dict[str, Any]
    ) -> AbuseAssessment:
        """
        Evaluate operational abuse risk.
        """

        signals: Dict[str, Any] = {}
        reasons = []
        abuse_score = 0.0

        try:
            unresolved_repeats = int(
                triage_context.get("unresolved_repeat_count", 0)
            )

            total_tickets = int(
                triage_context.get("total_tickets", 0)
            )

            total_escalations = int(
                triage_context.get("total_escalations", 0)
            )

        except Exception:
            logger.exception("Invalid triage context supplied to abuse guard.")
            unresolved_repeats = 0
            total_tickets = 0
            total_escalations = 0



        if auth_context:
            failed_attempts = int(
                auth_context.get("failed_login_attempts", 0)
            )

            suspicious_flag = bool(
                auth_context.get("suspicious_flag", False)
            )

            account_locked = bool(
                auth_context.get("account_locked", False)
            )

            if failed_attempts >= self.CRITICAL_FAILED_LOGINS:
                signals["critical_failed_logins"] = failed_attempts
                abuse_score += 80.0
                reasons.append(
                    f"Critical failed login attempts ({failed_attempts})"
                )

            elif failed_attempts > self.MAX_SAFE_FAILED_LOGINS:
                signals["high_failed_logins"] = failed_attempts
                abuse_score += 40.0
                reasons.append(
                    f"High failed login attempts ({failed_attempts})"
                )

            if suspicious_flag:
                signals["suspicious_auth_flag"] = True
                abuse_score += 30.0
                reasons.append("Suspicious authentication state")

            if account_locked:
                signals["account_locked"] = True
                abuse_score += 10.0
                reasons.append("Account currently locked")



        if unresolved_repeats >= self.MAX_UNRESOLVED_REPEATS:
            signals["ticket_spam_detected"] = unresolved_repeats
            abuse_score += 60.0
            reasons.append(
                f"Repeated unresolved ticket activity ({unresolved_repeats})"
            )



        if (
            total_tickets > 0
            and total_escalations >= self.ESCALATION_ABUSE_MIN_COUNT
        ):
            escalation_ratio = total_escalations / total_tickets

            if escalation_ratio > self.ESCALATION_ABUSE_RATIO:
                signals["escalation_abuse_ratio"] = escalation_ratio
                signals["total_escalations"] = total_escalations

                abuse_score += 30.0

                reasons.append(
                    f"High escalation frequency ({escalation_ratio:.2f})"
                )


        abuse_score = max(0.0, min(100.0, abuse_score))

        abuse_detected = abuse_score >= self.ABUSE_SCORE_THRESHOLD

        final_reason = (
            " | ".join(reasons)
            if reasons
            else "No abuse indicators detected"
        )

        if abuse_detected:
            logger.warning(
                "Operational abuse detected score=%s reason=%s",
                abuse_score,
                final_reason
            )

        return AbuseAssessment(
            abuse_detected=abuse_detected,
            abuse_score=abuse_score,
            signals=signals,
            reason=final_reason
        )