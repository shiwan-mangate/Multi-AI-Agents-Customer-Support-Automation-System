from datetime import datetime, UTC
from typing import Any
from layer_2_proactive_agent.schemas.proactive_state import (
    ProactiveState,
)
from layer_2_proactive_agent.utils.logger import (
    logger,
)
from layer_2_proactive_agent.services.risk_engine import (
    RiskEngine,
)
risk_engine = RiskEngine()
def risk_scoring_node(
    state: ProactiveState,
) -> dict[str, Any]:
    """
    Computes final business risk assessment
    from signal intelligence and CRM profile.
    """

    workflow_id = state["workflow_id"]

    signal_assessment = state["signal_assessment"]
    customer_profile = state["customer_profile"]

    logger.info(
        "Status=START | "
        "Node=RISK_SCORING | "
        "Workflow=%s",
        workflow_id,
    )

    timestamp = datetime.now(UTC).isoformat()

    try:

        if signal_assessment is None:
            raise ValueError(
                "Missing signal_assessment."
            )

        if customer_profile is None:
            raise ValueError(
                "Missing customer_profile."
            )

        risk_assessment = (
            risk_engine.assess(
                signal_assessment=signal_assessment,
                customer_profile=customer_profile,
            )
        )

        if risk_assessment is None:
            raise ValueError(
                "Risk assessment failed."
            )

        logger.info(
            "Status=SUCCESS | "
            "Node=RISK_SCORING | "
            "Workflow=%s | "
            "RiskLevel=%s | "
            "RiskScore=%s | "
            "Escalation=%s",
            workflow_id,
            risk_assessment.risk_level.value,
            risk_assessment.risk_score,
            risk_assessment.escalation_candidate,
        )

        return {
            "risk_assessment": risk_assessment,
            "current_node": "risk_scoring_node",
            "workflow_logs": [
                {
                    "timestamp": timestamp,
                    "node": "risk_scoring_node",
                    "message": (
                        f"Risk assessed "
                        f"level="
                        f"{risk_assessment.risk_level.value} "
                        f"score="
                        f"{risk_assessment.risk_score}"
                    ),
                }
            ],
        }

    except Exception as exc:

        logger.exception(
            "Status=FAILED | "
            "Node=RISK_SCORING | "
            "Workflow=%s | "
            "Error=%s",
            workflow_id,
            str(exc),
        )

        raise