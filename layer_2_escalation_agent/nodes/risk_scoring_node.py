import logging
from datetime import datetime, UTC

from layer_2_escalation_agent.schemas.escalation_state import EscalationState
from layer_2_escalation_agent.services.risk_engine import RiskEngine

logger = logging.getLogger(__name__)


def risk_scoring_node(
    state: EscalationState,
    risk_engine=None
) -> EscalationState:
    """
    Calculate escalation severity intelligence.

    Supports clean Dependency Injection from the global orchestration container 
    with a seamless local instance fallback.
    """
    logger.info("Executing risk_scoring_node")

    state["current_node"] = "risk_scoring_node"

    trigger_assessment = state["trigger_assessment"]
    customer_context = state["customer_context"]
    conversation_context = state["conversation_context"]

    missing = []

    if not trigger_assessment:
        missing.append("trigger_assessment")

    if not customer_context:
        missing.append("customer_context")

    if not conversation_context:
        missing.append("conversation_context")

    if missing:
        error_msg = (
            f"Risk scoring failed. Missing required context: {missing}"
        )
        logger.error(error_msg)
        state["errors"].append(error_msg)
        raise ValueError(error_msg)

    # 1. Resolve Risk Engine Dependency via Injection or Fallback
    engine = risk_engine or RiskEngine()

    repeat_issue_count = getattr(customer_context, "repeat_issue_count", 0)
    current_sentiment = state.get("initial_sentiment", "neutral")

    # 2. Execute Risk Calculation Sequence
    assessment = engine.assess(
        trigger_assessment=trigger_assessment,
        customer_context=customer_context,
        repeat_issue_count=repeat_issue_count,
        current_sentiment=current_sentiment,
    )

    risk_level_str = assessment.level.value if hasattr(assessment.level, "value") else str(assessment.level)

    logger.info(
        "Risk assessment complete | ticket_id=%s | score=%.1f | level=%s",
        state["ticket_id"],
        assessment.score,
        risk_level_str,
    )

    state["risk_assessment"] = assessment

    # 3. Log Telemetry Entry
    log_entry = {
        "node": "risk_scoring_node",
        "timestamp": datetime.now(UTC).isoformat(),
        "message": "Risk assessment completed.",
        "data": {
            "score": assessment.score,
            "level": risk_level_str,
            "legal_risk": assessment.legal_risk,
            "security_risk": assessment.security_risk,
            "churn_risk": assessment.churn_risk,
            "sla_risk": assessment.sla_risk,
        },
    }

    state["workflow_logs"].append(log_entry)

    return state