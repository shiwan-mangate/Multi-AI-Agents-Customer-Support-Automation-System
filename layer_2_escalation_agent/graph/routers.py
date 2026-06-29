import logging

from layer_2_escalation_agent.schemas.escalation_state import EscalationState
from layer_2_escalation_agent.schemas.escalation_response import EscalationResponse

logger = logging.getLogger(__name__)


def route_validation(state: EscalationState) -> str:
    """
    Route after contract validation.
    
    Note: Since validate_contract_node executes an explicit fail-fast raise
    on invalid inputs, this path will deterministically transition to "valid".
    """
    if state.get("errors"):
        logger.warning(
            "Validation routing -> invalid fallback triggered | ticket_id=%s | errors=%s",
            state.get("ticket_id"),
            state.get("errors"),
        )
        return "invalid"

    logger.info(
        "Validation routing -> valid | ticket_id=%s",
        state.get("ticket_id"),
    )
    return "valid"


def route_duplicate_case(state: EscalationState) -> str:
    """
    Route after trigger assessment.

    Returns:
        "duplicate" or "continue"
    """
    trigger_assessment = state.get("trigger_assessment")

    if not trigger_assessment:
        logger.error(
            "Duplicate router missing trigger_assessment | ticket_id=%s",
            state.get("ticket_id"),
        )
        raise ValueError("Missing trigger_assessment in duplicate router.")

    if trigger_assessment.duplicate_case_detected:
        logger.info(
            "Duplicate routing -> duplicate | ticket_id=%s | case_id=%s",
            state.get("ticket_id"),
            trigger_assessment.existing_case_id,
        )

        # Refactored: Hydrate a valid EscalationResponse object instead of a raw dictionary
        # to ensure downstream validation contracts match your schemas seamlessly
        state["response"] = EscalationResponse(
            status="DUPLICATE_SUPPRESSED",
            case_id=trigger_assessment.existing_case_id,
            priority=None,
            assigned_team=None,
            holding_sent=False
        )

        return "duplicate"

    logger.info(
        "Duplicate routing -> continue | ticket_id=%s",
        state.get("ticket_id"),
    )

    return "continue"