import logging
from datetime import datetime, UTC

from layer_2_escalation_agent.schemas.escalation_state import EscalationState
from layer_2_escalation_agent.services.holding_response_service import HoldingResponseService

logger = logging.getLogger(__name__)


def holding_response_node(
    state: EscalationState,
    holding_response_service=None
) -> EscalationState:
    """
    Generate customer-facing holding response.

    Supports clean Dependency Injection from the global orchestration container 
    with a seamless local instance fallback.
    """
    logger.info("Executing holding_response_node")

    state["current_node"] = "holding_response_node"

    ticket_id = state["ticket_id"]

    fallback_message = (
        "Your case has been escalated for specialist review. "
        "We already have your details and will follow up as soon as possible."
    )

    holding_message = fallback_message
    degraded = False

    risk_assessment = state.get("risk_assessment")
    routing_decision = state.get("routing_decision")
    trigger_assessment = state.get("trigger_assessment")
    customer_context = state.get("customer_context")

    missing = []

    if not risk_assessment:
        missing.append("risk_assessment")

    if not routing_decision:
        missing.append("routing_decision")

    if not trigger_assessment:
        missing.append("trigger_assessment")

    if not customer_context:
        missing.append("customer_context")

    if missing:
        degraded = True
        logger.error(
            "Holding response degraded | ticket_id=%s | missing=%s",
            ticket_id,
            missing,
        )

    else:
        try:
            # 1. Resolve Holding Response Service Dependency via Injection or Fallback
            service = holding_response_service or HoldingResponseService()

            # 2. Execute Holding Message Generation Contract Logic
            holding_message = service.generate(
                risk_assessment=risk_assessment,
                routing_decision=routing_decision,
                trigger_assessment=trigger_assessment,
                customer_context=customer_context,
                channel="chat",
            )

            logger.info(
                "Holding response generated | ticket_id=%s",
                ticket_id,
            )

        except Exception as exc:
            degraded = True
            logger.error(
                "Holding response generation failed fallback active | ticket_id=%s | error=%s",
                ticket_id,
                str(exc),
            )

    state["holding_message"] = holding_message

    preview = (
        holding_message[:100] + "..."
        if len(holding_message) > 100
        else holding_message
    )

    # 3. Log Telemetry Entry
    log_entry = {
        "node": "holding_response_node",
        "timestamp": datetime.now(UTC).isoformat(),
        "message": (
            "Fallback holding response used."
            if degraded
            else "Holding response generated successfully."
        ),
        "data": {
            "holding_message_preview": preview,
            "degraded": degraded,
        },
    }

    state["workflow_logs"].append(log_entry)

    return state