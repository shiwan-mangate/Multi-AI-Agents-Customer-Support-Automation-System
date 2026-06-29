from datetime import datetime, UTC
from typing import Any, Dict

from layer_2_proactive_agent.schemas.proactive_state import (
    ProactiveState,
)

from layer_2_proactive_agent.utils.logger import (
    logger,
)

from layer_2_proactive_agent.services.outreach_decision_service import (
    OutreachDecisionService,
)

decision_service = OutreachDecisionService()


def outreach_decision_node(
    state: ProactiveState,
) -> Dict[str, Any]:
    """
    Evaluates computed risk and determines
    the final workflow action.
    """

    workflow_id = state["workflow_id"]
    risk_assessment = state["risk_assessment"]

    logger.info(
        "Status=START | "
        "Node=OUTREACH_DECISION | "
        "Workflow=%s",
        workflow_id,
    )

    timestamp = datetime.now(UTC).isoformat()

    try:

        if risk_assessment is None:
            raise ValueError(
                "Missing risk_assessment in state."
            )

        decision = (
            decision_service.decide(
                risk_assessment=risk_assessment
            )
        )

        logger.info(
            "Status=SUCCESS | "
            "Node=OUTREACH_DECISION | "
            "Workflow=%s | "
            "Action=%s",
            workflow_id,
            decision.action.value,
        )

        return {
            "decision": decision,
            "current_node":
                "outreach_decision_node",
            "workflow_logs": [
                {
                    "timestamp": timestamp,
                    "node":
                        "outreach_decision_node",
                    "message": (
                        f"Decision reached: "
                        f"{decision.action.value} "
                        f"({decision.reason})"
                    ),
                }
            ],
        }

    except Exception as exc:

        logger.exception(
            "Status=FAILED | "
            "Node=OUTREACH_DECISION | "
            "Workflow=%s | Error=%s",
            workflow_id,
            str(exc),
        )

        raise