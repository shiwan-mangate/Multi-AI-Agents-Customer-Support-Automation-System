import logging
from datetime import datetime, UTC

from layer_2_escalation_agent.schemas.escalation_state import EscalationState
from layer_2_escalation_agent.schemas.escalation_response import EscalationResponse

logger = logging.getLogger(__name__)


def response_node(state: EscalationState) -> EscalationState:
    """
    Build final external API response contract.

    Responsibilities:
    - convert internal workflow state into clean public response
    - handle duplicate suppression responses
    - persist typed EscalationResponse into state
    """
    logger.info("Executing response_node")

    state["current_node"] = "response_node"

    trigger_assessment = state["trigger_assessment"]

    if trigger_assessment.duplicate_case_detected:
        existing_case_id = trigger_assessment.existing_case_id
        state["case_id"] = existing_case_id

        response = EscalationResponse(
            status="DUPLICATE_SUPPRESSED",
            case_id=existing_case_id,
            priority=None,
            assigned_team=None,
            holding_sent=False,
        )

        state["response"] = response

        state["workflow_logs"].append({
            "node": "response_node",
            # Refactored: Aligned timestamp module to standard UTC singletons
            "timestamp": datetime.now(UTC).isoformat(),
            "message": "Duplicate escalation suppressed.",
            "data": {
                "status": "DUPLICATE_SUPPRESSED",
                "case_id": existing_case_id,
            }
        })

        return state

    case_id = state["case_id"]
    risk_assessment = state["risk_assessment"]
    routing_decision = state["routing_decision"]

    # Refactored: Safely resolve primitive string token values across both types
    priority_level = risk_assessment.level.value if hasattr(risk_assessment.level, "value") else str(risk_assessment.level)

    try:
        response = EscalationResponse(
            status="ESCALATED",
            case_id=case_id,
            priority=priority_level,
            assigned_team=routing_decision.assigned_team,
            holding_sent=state.get("holding_sent", False),
        )

        logger.info(
            "Final response generated | case_id=%s | team=%s",
            case_id,
            routing_decision.assigned_team,
        )

    except Exception as exc:
        error_msg = f"Response generation failed: {str(exc)}"
        logger.error(error_msg)
        state["errors"].append(error_msg)
        raise ValueError(error_msg)

    state["response"] = response

    state["workflow_logs"].append({
        "node": "response_node",
        # Refactored: Standardized timestamp format signature to match global UTC module layouts
        "timestamp": datetime.now(UTC).isoformat(),
        "message": "Final API response generated.",
        "data": {
            "status": "ESCALATED",
            "case_id": case_id,
            "priority": priority_level,
            "assigned_team": routing_decision.assigned_team,
        }
    })

    return state