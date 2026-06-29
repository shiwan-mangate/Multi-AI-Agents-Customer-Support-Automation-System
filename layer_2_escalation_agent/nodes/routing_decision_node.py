import logging
from datetime import datetime, UTC

from layer_2_escalation_agent.schemas.escalation_state import EscalationState
from layer_2_escalation_agent.services.routing_service import RoutingService

logger = logging.getLogger(__name__)


def routing_decision_node(
    state: EscalationState,
    routing_service=None
) -> EscalationState:
    """
    Determine human ownership queue and SLA deadline.

    Supports clean Dependency Injection from the global orchestration container 
    with a seamless local instance fallback.
    """
    logger.info("Executing routing_decision_node")

    state["current_node"] = "routing_decision_node"

    trigger_assessment = state["trigger_assessment"]
    risk_assessment = state["risk_assessment"]
    customer_context = state["customer_context"]
    source_agent = state["source_agent"]

    missing = []

    if not trigger_assessment:
        missing.append("trigger_assessment")

    if not risk_assessment:
        missing.append("risk_assessment")

    if not customer_context:
        missing.append("customer_context")

    if missing:
        error_msg = (
            "Routing decision failed. Missing required context: "
            + ", ".join(missing)
        )
        logger.error(error_msg)
        state["errors"].append(error_msg)
        raise ValueError(error_msg)

    # 1. Resolve Routing Service Dependency via Injection or Fallback
    service = routing_service or RoutingService()

    # 2. Execute Routing Decision Contract Logic
    decision = service.decide(
        trigger_assessment=trigger_assessment,
        risk_assessment=risk_assessment,
        customer_context=customer_context,
        source_agent=source_agent,
    )

    logger.info(
        "Routing complete | ticket_id=%s | team=%s | deadline=%s",
        state["ticket_id"],
        decision.assigned_team,
        decision.sla_deadline.isoformat(),
    )

    state["routing_decision"] = decision

    risk_level_str = risk_assessment.level.value if hasattr(risk_assessment.level, "value") else str(risk_assessment.level)

    # 3. Log Telemetry Entry
    log_entry = {
        "node": "routing_decision_node",
        "timestamp": datetime.now(UTC).isoformat(),
        "message": "Routing decision completed.",
        "data": {
            "assigned_team": decision.assigned_team,
            "sla_deadline": decision.sla_deadline.isoformat(),
            "risk_level": risk_level_str,
        },
    }

    state["workflow_logs"].append(log_entry)

    return state