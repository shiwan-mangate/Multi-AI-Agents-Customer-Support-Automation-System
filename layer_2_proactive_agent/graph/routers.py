from layer_2_proactive_agent.schemas.proactive_state import ProactiveState
from layer_2_proactive_agent.schemas.enums import OutreachAction
from layer_2_proactive_agent.utils.logger import logger


def suppression_router(state: ProactiveState) -> str:
    """Routes suppressed workflows directly to the boundary response node."""
    workflow_id = state["workflow_id"]
    suppressed = state.get("suppressed", False)

    if suppressed:
        logger.info(
            "Router=SUPPRESSION | Workflow=%s | Decision=SUPPRESSED | Route=response_node",
            workflow_id,
        )
        return "response_node"

    logger.info(
        "Router=SUPPRESSION | Workflow=%s | Decision=PROCEED | Route=signal_analysis_node",
        workflow_id,
    )
    return "signal_analysis_node"


def decision_router(state: ProactiveState) -> str:
    """Routes based on the final outreach decision."""
    workflow_id = state["workflow_id"]
    decision = state.get("decision")

    if decision is None:
        raise ValueError("Decision router received state without decision.")

    if decision.action == OutreachAction.OUTREACH:
        logger.info(
            "Router=DECISION | Workflow=%s | Action=OUTREACH | Route=message_generation_node",
            workflow_id,
        )
        return "message_generation_node"

    if decision.action == OutreachAction.ESCALATE:
        logger.info(
            "Router=DECISION | Workflow=%s | Action=ESCALATE | Route=escalation_handoff_node",
            workflow_id,
        )
        return "escalation_handoff_node"

    logger.info(
        "Router=DECISION | Workflow=%s | Action=NO_ACTION | Route=response_node",
        workflow_id,
    )
    return "response_node"