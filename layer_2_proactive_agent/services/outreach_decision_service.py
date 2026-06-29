from layer_2_proactive_agent.schemas.risk_assessment import (
    RiskAssessment,
)

from layer_2_proactive_agent.schemas.outreach_decision import (
    OutreachDecision,
)

from layer_2_proactive_agent.schemas.enums import (
    OutreachAction,
    RiskLevel,
)

from layer_2_proactive_agent.utils.logger import (
    logger,
)


class OutreachDecisionService:
    """
    Determines the final proactive workflow
    action from business risk assessment.
    """

    OUTREACH_CONFIDENCE = 0.85
    ESCALATION_CONFIDENCE = 1.0
    NO_ACTION_CONFIDENCE = 1.0

    def decide(
        self,
        risk_assessment: RiskAssessment,
    ) -> OutreachDecision:

        logger.info(
            "Status=START | "
            "Operation=OUTREACH_DECISION | "
            "RiskLevel=%s",
            risk_assessment.risk_level.value,
        )

        if risk_assessment.escalation_candidate:

            decision = OutreachDecision(
                action=OutreachAction.ESCALATE,
                reason=(
                    "Customer requires immediate "
                    "escalation review based on "
                    "critical risk thresholds."
                ),
                confidence=self.ESCALATION_CONFIDENCE,
                review_required=True,
            )

        elif risk_assessment.risk_level in (
            RiskLevel.HIGH,
            RiskLevel.MEDIUM,
        ):

            decision = OutreachDecision(
                action=OutreachAction.OUTREACH,
                reason=(
                    f"Customer exhibits "
                    f"{risk_assessment.risk_level.value.lower()} "
                    f"risk, warranting proactive outreach."
                ),
                confidence=self.OUTREACH_CONFIDENCE,
                review_required=False,
            )

        else:

            decision = OutreachDecision(
                action=OutreachAction.NO_ACTION,
                reason=(
                    "Customer risk is below the "
                    "active outreach threshold."
                ),
                confidence=self.NO_ACTION_CONFIDENCE,
                review_required=False,
            )

        logger.info(
            "Status=SUCCESS | "
            "Operation=OUTREACH_DECISION | "
            "Action=%s",
            decision.action.value,
        )

        return decision