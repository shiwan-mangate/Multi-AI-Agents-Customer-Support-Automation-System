import logging
from datetime import datetime, UTC

from layer_2_escalation_agent.schemas.escalation_state import EscalationState
from layer_2_escalation_agent.schemas.human_decision import HumanDecisionType
from layer_2_escalation_agent.services.notification_service import NotificationService

logger = logging.getLogger(__name__)


def notification_dispatch_node(
    state: EscalationState,
    notification_service=None
) -> EscalationState:
    """
    Build outbox-ready notification jobs for approved escalations.

    Supports clean Dependency Injection from the global orchestration container 
    with a seamless local instance fallback.
    """
    logger.info("Executing notification_dispatch_node")

    state["current_node"] = "notification_dispatch_node"

    ticket_id = str(state["ticket_id"]).strip()
    case_id = state["case_id"]

    human_brief = state.get("human_brief")
    routing_decision = state.get("routing_decision")
    human_decision = state.get("human_decision")
    risk_assessment = state.get("risk_assessment")
    customer_context = state.get("customer_context")
    trigger_assessment = state.get("trigger_assessment")

    missing = []

    if not human_brief:
        missing.append("human_brief")

    if not routing_decision:
        missing.append("routing_decision")

    if not risk_assessment:
        missing.append("risk_assessment")

    if not customer_context:
        missing.append("customer_context")

    if not trigger_assessment:
        missing.append("trigger_assessment")

    if missing:
        error_msg = (
            "Notification dispatch failed. Missing required context: "
            + ", ".join(missing)
        )
        logger.error(error_msg)
        state["errors"].append(error_msg)
        raise ValueError(error_msg)

    # Governance safety
    if human_decision is None:
        error_msg = "Notification blocked. Missing governance decision."
        logger.error("%s | ticket_id=%s", error_msg, ticket_id)
        state["errors"].append(error_msg)
        raise ValueError(error_msg)

    # =======================================================
    # 🟢 DEFENSIVE EXTRACTOR: Protects against checkpoint dicts
    # =======================================================
    if isinstance(human_decision, dict):
        decision_str = human_decision.get("decision")
    else:
        decision_str = (
            human_decision.decision.value 
            if hasattr(human_decision.decision, "value") 
            else str(human_decision.decision)
        )
        
    normalized_decision = str(decision_str).strip().upper() if decision_str else ""

    if normalized_decision not in ["APPROVE", "OVERRIDE"]:
        error_msg = (
            f"Notification blocked. Invalid governance decision: {decision_str}"
        )
        logger.error(error_msg)
        state["errors"].append(error_msg)
        raise ValueError(error_msg)

    # 1. Resolve Notification Service Dependency via Injection or Fallback
    service = notification_service or NotificationService()

    # 2. Execute Notification Job Compilation
    jobs = service.build_jobs(
        case_id=case_id,
        ticket_id=ticket_id,
        human_brief=human_brief,
        routing_decision=routing_decision,
        risk_assessment=risk_assessment,
        customer_context=customer_context,
        trigger_assessment=trigger_assessment,
    )

    if not jobs:
        error_msg = "NotificationService generated zero jobs."
        logger.error("%s | ticket_id=%s", error_msg, ticket_id)
        state["errors"].append(error_msg)
        raise ValueError(error_msg)

    state["notification_jobs"] = jobs

    # 3. Log Telemetry Entry
    state["workflow_logs"].append({
        "node": "notification_dispatch_node",
        "timestamp": datetime.now(UTC).isoformat(),
        "message": "Notification jobs staged for outbox delivery.",
        "data": {
            "job_count": len(jobs),
            "channels": [
                job.channel.value if hasattr(job.channel, "value") else str(job.channel)
                for job in jobs
            ],
        },
    })

    logger.info(
        "Notification staging complete | ticket_id=%s | jobs=%s",
        ticket_id,
        len(jobs),
    )

    return state