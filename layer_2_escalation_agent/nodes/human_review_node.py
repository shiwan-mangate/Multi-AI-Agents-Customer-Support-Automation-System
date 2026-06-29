import logging
from datetime import datetime, UTC

from layer_2_escalation_agent.schemas.escalation_state import EscalationState
from layer_2_escalation_agent.schemas.human_decision import HumanDecision, HumanDecisionType

logger = logging.getLogger(__name__)


def human_review_node(state: EscalationState) -> EscalationState:
    """
    Human governance checkpoint.
    Processes the injected human decision following an orchestrator workflow resume.
    """
    logger.info("Executing human_review_node")
    logger.warning(
    "ENTERED HUMAN REVIEW NODE | ticket=%s",
    state["ticket_id"]
)

    state["current_node"] = "human_review_node"

    # =======================================================
    # 🟢 1. VALIDATE INJECTED DECISION
    # =======================================================
    decision_data = state.get("human_decision")
    logger.warning(
        "HUMAN DECISION RECEIVED = %s",
        decision_data
    )

    if not decision_data:
        raise ValueError(
            "Human decision missing. Workflow resumed incorrectly."
        )

    # =======================================================
    # 🟢 2. HYDRATE PYDANTIC MODEL (Protects against Checkpoint Dicts)
    # =======================================================
    if isinstance(decision_data, dict):
        decision_value = decision_data.get("decision")
        if isinstance(decision_value, str):
            decision_data["decision"] = HumanDecisionType(decision_value.lower())
        decision = HumanDecision(**decision_data)
    else:
        decision = decision_data

    decision_type_str = decision.decision.value if hasattr(decision.decision, "value") else str(decision.decision)
    routing_decision = state.get("routing_decision")


    # =======================================================
    # 🟢 3. PROCESS DECISION BRANCHES
    # =======================================================
    if decision_type_str.upper() == "OVERRIDE":
        if decision.override_team and routing_decision:
            routing_decision.assigned_team = decision.override_team
        if decision.override_priority and routing_decision:
            routing_decision.priority = decision.override_priority

    elif decision_type_str.upper() == "REJECT":
        raise ValueError("Escalation rejected by human reviewer.")

    elif decision_type_str.upper() == "HOLD":
        raise ValueError("Escalation placed on hold by human reviewer.")

    # =======================================================
    # 🟢 4. FINALIZE STATE
    # =======================================================
    state["human_decision"] = decision
    state["review_required"] = True
    state["review_completed"] = True

    state["workflow_logs"].append({
        "node": "human_review_node",
        "timestamp": datetime.now(UTC).isoformat(),
        "message": "Human review decision processed successfully.",
        "data": {
            "decision": decision_type_str,
            "reviewer_id": decision.reviewer_id,
        },
    })

    logger.info(
        "Human review processed | ticket_id=%s | decision=%s",
        state["ticket_id"],
        decision_type_str,
    )

    return state