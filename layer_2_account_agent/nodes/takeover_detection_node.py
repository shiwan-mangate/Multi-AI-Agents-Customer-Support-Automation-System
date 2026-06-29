from layer_2_account_agent.schemas.account_state import AccountState
from layer_2_account_agent.schemas.domain import WorkflowLog, TakeoverAssessment
from layer_2_account_agent.services.takeover_detector import TakeoverDetectorService
import logging
from typing import Dict, Any
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

takeover_detector_service = TakeoverDetectorService()


def takeover_detection(
    state: AccountState
) -> Dict[str, Any]:
    """
    Detect account takeover patterns.
    """

    ticket_id = state.get("ticket_id")
    auth_context = state.get("auth_context")
    requested_action = state.get("requested_action")
    logs = list(state.get("workflow_logs", []))

    logger.info(
        "Executing takeover_detection node ticket_id=%s",
        ticket_id
    )

    if not requested_action:
        fallback = TakeoverAssessment(
            takeover_detected=False,
            risk_score_modifier=0.0,
            signals={},
            reason="No requested action available"
        )

        logs.append(
            WorkflowLog(
                node="takeover_detection_node",
                message="Missing requested action. Safe fallback applied.",
                timestamp=datetime.now(timezone.utc),
                data={"ticket_id": ticket_id}
            )
        )

        return {
            "takeover_assessment": fallback,
            "workflow_logs": logs,
            "current_node": "takeover_detection_node"
        }

    try:
        result = takeover_detector_service.evaluate_takeover_risk(
            auth_context=auth_context,
            requested_action=requested_action
        )

        logs.append(
            WorkflowLog(
                node="takeover_detection_node",
                message=(
                    f"Takeover detection complete "
                    f"detected={result.takeover_detected} "
                    f"score={result.risk_score_modifier}"
                ),
                timestamp=datetime.now(timezone.utc),
                data={
                    "ticket_id": ticket_id,
                    "reason": result.reason
                }
            )
        )

        return {
            "takeover_assessment": result,
            "workflow_logs": logs,
            "current_node": "takeover_detection_node"
        }

    except Exception:
        logger.exception(
            "Takeover detection failed ticket_id=%s",
            ticket_id
        )

        fallback = TakeoverAssessment(
            takeover_detected=False,
            risk_score_modifier=0.0,
            signals={"system_failure": True},
            reason="Takeover detection unavailable"
        )

        logs.append(
            WorkflowLog(
                node="takeover_detection_node",
                message="Takeover detection failed. Safe fallback applied.",
                timestamp=datetime.now(timezone.utc),
                data={"ticket_id": ticket_id}
            )
        )

        return {
            "takeover_assessment": fallback,
            "workflow_logs": logs,
            "current_node": "takeover_detection_node"
        }