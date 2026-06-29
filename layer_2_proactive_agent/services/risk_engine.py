from decimal import Decimal

from layer_2_proactive_agent.schemas.signal_assessment import (
    SignalAssessment,
)

from layer_2_proactive_agent.schemas.risk_assessment import (
    RiskAssessment,
)

from layer_2_proactive_agent.schemas.enums import (
    RiskLevel,
)

from crm_agent.schemas.customer_profile import (
    CustomerProfile,
)

from layer_2_proactive_agent.utils.logger import (
    logger,
)


class RiskEngine:
    """
    Computes final business risk assessment
    from signal intelligence and CRM profile.
    """

    SEVERITY_SCORES = {
        RiskLevel.LOW: 10,
        RiskLevel.MEDIUM: 30,
        RiskLevel.HIGH: 60,
        RiskLevel.URGENT: 90,
    }

    CHURN_SCORES = {
    "low": 10,
    "medium": 30,
    "high": 60,
    "urgent": 90,
    "critical": 90,
}

    TIER_SCORES = {
        "standard": 0,
        "premium": 10,
        "enterprise": 20,
    }

    def assess(
        self,
        signal_assessment: SignalAssessment,
        customer_profile: CustomerProfile,
    ) -> RiskAssessment:
        """
        Produce final RiskAssessment.
        """

        logger.info(
            "Status=START | "
            "Operation=RISK_ASSESSMENT | "
            "Customer=%s",
            customer_profile.customer_id,
        )

        risk_reasons: list[str] = []


        severity_score = self.SEVERITY_SCORES[
            signal_assessment.severity
        ]

        risk_reasons.append(
            f"Signal severity={signal_assessment.severity.value}"
        )



        churn_level = (
            customer_profile
            .churn_intelligence
            .churn_level
        )

        churn_score = self.CHURN_SCORES.get(
                churn_level,
                10,
            )

        risk_reasons.append(
            f"Customer churn level={churn_level}"
        )


        tier_score = self.TIER_SCORES.get(
            customer_profile.tier,
            0,
        )

        risk_reasons.append(
            f"Customer tier={customer_profile.tier}"
        )



        history_score = min(
            customer_profile.negative_ticket_count * 2,
            20,
        )

        if history_score:
            risk_reasons.append(
                f"Negative ticket history={customer_profile.negative_ticket_count}"
            )


        total_score = min(
            severity_score
            + churn_score
            + tier_score
            + history_score,
            100,
        )



        if total_score >= 80:
            risk_level = RiskLevel.URGENT

        elif total_score >= 60:
            risk_level = RiskLevel.HIGH

        elif total_score >= 40:
            risk_level = RiskLevel.MEDIUM

        else:
            risk_level = RiskLevel.LOW



        escalation_candidate = False

        if risk_level == RiskLevel.URGENT:
            escalation_candidate = True

            risk_reasons.append(
                "Urgent risk threshold exceeded"
            )

        elif (
            customer_profile.tier == "enterprise"
            and risk_level == RiskLevel.HIGH
        ):
            escalation_candidate = True

            risk_reasons.append(
                "Enterprise customer with high risk"
            )

        assessment = RiskAssessment(
            risk_level=risk_level,
            risk_score=Decimal(
                str(round(total_score, 2))
            ),
            risk_reasons=risk_reasons,
            escalation_candidate=escalation_candidate,
        )

        logger.info(
            "Status=SUCCESS | "
            "Customer=%s | "
            "RiskLevel=%s | "
            "RiskScore=%s | "
            "Escalation=%s",
            customer_profile.customer_id,
            assessment.risk_level.value,
            assessment.risk_score,
            assessment.escalation_candidate,
        )

        return assessment