import logging

from datetime import datetime, UTC
from decimal import Decimal
from typing import List, Tuple

from crm_agent.db.models.customer_profile_model import (
    CustomerProfile,
)

from crm_agent.schemas.crm_event import CRMResolvedEvent

from crm_agent.schemas.churn import (
    ChurnAssessment,
    ChurnComputationBreakdown,
)


logger = logging.getLogger(__name__)


class ChurnEngine:
    """
    Deterministic churn risk calculator.
    Pure business logic.
    No database side-effects.
    """

    def __init__(self):
        self.MAX_SCORE = Decimal("100.00")

        self.WEIGHT_FAILURE = Decimal("10.00")
        self.WEIGHT_ESCALATION = Decimal("15.00")
        self.WEIGHT_DENIAL = Decimal("5.00")

        self.VIP_MULTIPLIER = Decimal("1.30")

        self.INACTIVITY_THRESHOLD_DAYS = 60

    def calculate_churn_risk(
        self,
        profile: CustomerProfile,
        event: CRMResolvedEvent,
    ) -> ChurnAssessment:

        total_score = Decimal("0.00")
        risk_reasons: List[str] = []

        negative_score, negative_reasons = (
            self._calculate_negative_ticket_score(
                profile
            )
        )
        total_score += negative_score
        risk_reasons.extend(negative_reasons)

        escalation_score, escalation_reasons = (
            self._calculate_escalation_score(
                profile
            )
        )
        total_score += escalation_score
        risk_reasons.extend(escalation_reasons)

        sentiment_score, sentiment_reasons = (
            self._calculate_sentiment_score(
                profile,
                event,
            )
        )
        total_score += sentiment_score
        risk_reasons.extend(sentiment_reasons)

        inactivity_score, inactivity_reasons = (
            self._calculate_inactivity_score(
                profile
            )
        )
        total_score += inactivity_score
        risk_reasons.extend(inactivity_reasons)

        final_score, vip_reasons = (
            self._apply_vip_multiplier(
                profile,
                total_score,
            )
        )
        risk_reasons.extend(vip_reasons)

        final_score = min(
            final_score,
            self.MAX_SCORE,
        )

        churn_level = (
            self._determine_churn_level(
                final_score
            )
        )

        final_reasons = (
            self._generate_risk_reasons(
                risk_reasons,
                churn_level,
            )
        )

        logger.info(
            "Churn calculated | customer_id=%s | score=%s | level=%s",
            profile.customer_id,
            final_score,
            churn_level,
        )

        breakdown = ChurnComputationBreakdown(
            negative_ticket_score=negative_score,
            unresolved_score=Decimal("0.00"),
            sentiment_score=sentiment_score,
            escalation_score=escalation_score,
            inactivity_score=inactivity_score,
            vip_multiplier_applied=(
                self.VIP_MULTIPLIER
                if vip_reasons
                else Decimal("1.00")
            ),
            raw_score=total_score,
            final_score=final_score,
        )

        return ChurnAssessment(
            customer_id=profile.customer_id,
            churn_score=final_score,
            churn_level=churn_level,
            risk_reasons=final_reasons,
            breakdown=breakdown,
        )


    def _calculate_negative_ticket_score(
        self,
        profile: CustomerProfile,
    ) -> Tuple[Decimal, List[str]]:

        score = Decimal("0.00")
        reasons = []

        if profile.total_failures > 0:
            penalty = (
                Decimal(profile.total_failures)
                * self.WEIGHT_FAILURE
            )
            score += penalty
            reasons.append(
                f"{profile.total_failures} historical failures"
            )

        if profile.total_denials > 0:
            penalty = (
                Decimal(profile.total_denials)
                * self.WEIGHT_DENIAL
            )
            score += penalty
            reasons.append(
                f"{profile.total_denials} historical denials"
            )

        return score, reasons


    def _calculate_escalation_score(
        self,
        profile: CustomerProfile,
    ) -> Tuple[Decimal, List[str]]:

        score = Decimal("0.00")
        reasons = []

        if profile.total_escalations > 0:
            score += (
                Decimal(profile.total_escalations)
                * self.WEIGHT_ESCALATION
            )
            reasons.append(
                f"{profile.total_escalations} escalations"
            )

            if profile.total_escalations >= 3:
                score += Decimal("15.00")
                reasons.append(
                    "Chronic escalation pattern detected"
                )

        return score, reasons


    def _calculate_sentiment_score(
        self,
        profile: CustomerProfile,
        event: CRMResolvedEvent,
    ) -> Tuple[Decimal, List[str]]:

        score = Decimal("0.00")
        reasons = []

        sentiment = (
            event.analytics.sentiment_end
            if event.analytics
            else "neutral"
        )

        if sentiment == "angry":
            score += Decimal("25.00")
            reasons.append(
                "Latest interaction ended ANGRY"
            )
        elif sentiment == "frustrated":
            score += Decimal("15.00")
            reasons.append(
                "Latest interaction ended FRUSTRATED"
            )

        history = profile.sentiment_history or []

        if len(history) >= 2:
            last_two = history[-2:]
            if last_two == ["angry", "angry"]:
                score += Decimal("20.00")
                reasons.append(
                    "Repeated angry interactions"
                )
            elif "angry" in last_two and "frustrated" in last_two:
                score += Decimal("10.00")
                reasons.append(
                    "Degrading sentiment trend"
                )

        return score, reasons


    def _calculate_inactivity_score(
        self,
        profile: CustomerProfile,
    ) -> Tuple[Decimal, List[str]]:

        score = Decimal("0.00")
        reasons = []

        if not profile.last_ticket_at:
            return score, reasons

        days_inactive = (
            datetime.now(UTC)
            - profile.last_ticket_at
        ).days

        if days_inactive > self.INACTIVITY_THRESHOLD_DAYS:
            score += Decimal("20.00")
            reasons.append(
                f"High risk: Account inactivity exceeds "
                f"{self.INACTIVITY_THRESHOLD_DAYS} days "
                f"({days_inactive} days lapse)."
            )

        return score, reasons


    def _apply_vip_multiplier(
        self,
        profile: CustomerProfile,
        current_score: Decimal,
    ) -> Tuple[Decimal, List[str]]:

        reasons = []

        if current_score <= 0:
            return current_score, reasons

        is_vip = (
            profile.tier
            in ["enterprise", "premium"]
        )

        high_ltv = (
            profile.ltv > Decimal("5000.00")
        )

        if is_vip or high_ltv:
            boosted = (
                current_score
                * self.VIP_MULTIPLIER
            )
            reasons.append(
                f"VIP multiplier "
                f"{self.VIP_MULTIPLIER}x applied"
            )
            return boosted, reasons

        return current_score, reasons


    def _determine_churn_level(
        self,
        score: Decimal
    ) -> str:
        if score < Decimal("40.00"):
            return "low"
        if score < Decimal("70.00"):
            return "medium"
        if score < Decimal("90.00"):
            return "high"
        return "urgent"


    def _generate_risk_reasons(
        self,
        raw_reasons: List[str],
        level: str,
    ) -> List[str]:

        if level == "low" and not raw_reasons:
            return [
                "Healthy customer account"
            ]

        unique = list(
            dict.fromkeys(raw_reasons)
        )

        unique.sort(
            key=lambda x: (
                "multiplier"
                not in x.lower()
            )
        )

        return unique