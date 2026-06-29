import logging
from datetime import datetime, UTC

from layer_2_escalation_agent.schemas.escalation_state import EscalationState
from layer_2_escalation_agent.schemas.human_brief import (
    HumanBrief,
    EmotionalState,
    ChurnRiskLevel,
)
from layer_2_escalation_agent.services.brief_generation_service import HumanBriefService
from layer_2_escalation_agent.dependencies import get_llm_client

logger = logging.getLogger(__name__)


def _map_emotional_state(sentiment: str) -> EmotionalState:
    """
    Normalize sentiment string into HumanBrief enum.
    """
    sentiment = (sentiment or "").strip().lower()

    mapping = {
        "angry": EmotionalState.ANGRY,
        "frustrated": EmotionalState.FRUSTRATED,
        "neutral": EmotionalState.NEUTRAL,
        "positive": EmotionalState.POSITIVE,
        "urgent": EmotionalState.FRUSTRATED, 
        "hostile": EmotionalState.ANGRY,
    }

    return mapping.get(sentiment, EmotionalState.NEUTRAL)


def brief_generation_node(
    state: EscalationState,
    human_brief_service=None
) -> EscalationState:
    """
    Generate human handoff intelligence brief.

    Supports clean Dependency Injection from the global orchestration container 
    with a seamless local instance fallback.
    """
    logger.info("Executing brief_generation_node")

    state["current_node"] = "brief_generation_node"

    ticket_id = state["ticket_id"]

    customer_context = state.get("customer_context")
    conversation_context = state.get("conversation_context")
    trigger_assessment = state.get("trigger_assessment")
    risk_assessment = state.get("risk_assessment")
    routing_decision = state.get("routing_decision")

    current_sentiment = state["initial_sentiment"]

    degraded = False
    degradation_reason = None

    missing = []

    if not customer_context:
        missing.append("customer_context")

    if not conversation_context:
        missing.append("conversation_context")

    if not trigger_assessment:
        missing.append("trigger_assessment")

    if not risk_assessment:
        missing.append("risk_assessment")

    if not routing_decision:
        missing.append("routing_decision")

    fallback_brief = HumanBrief(
        customer_summary="Customer intelligence unavailable.",
        issue_summary=(
            "Escalation triggered. Review transcript and workflow evidence."
        ),
        emotional_state=_map_emotional_state(current_sentiment),
        churn_risk_level=ChurnRiskLevel.MEDIUM,
        churn_reason=(
            "Automated churn assessment unavailable due to degraded workflow."
        ),
        attempted_actions=[
            "Trigger assessment completed",
            "Customer context enrichment attempted",
            "Conversation evidence assembly attempted",
            "Routing decision completed",
        ],
        blockers=[
            "System degradation prevented structured brief generation."
        ],
        recommended_next_action=(
            f"Review case manually via "
            f"{routing_decision.assigned_team if routing_decision else 'human_support_team'}."
        ),
        urgency_reason="Escalation workflow degraded.",
        brief_confidence=0.35,
    )

    brief = fallback_brief

    if missing:
        degraded = True
        degradation_reason = f"Missing context: {', '.join(missing)}"

        logger.error(
            "Brief generation degraded | ticket_id=%s | reason=%s",
            ticket_id,
            degradation_reason,
        )

    else:
        try:
            # 1. Resolve Human Brief Service Dependency via Injection or Fallback
            if human_brief_service is not None:
                service = human_brief_service
            else:
                llm_client = get_llm_client()
                service = HumanBriefService(llm_client=llm_client)

            # 2. Execute Structured AI Summary Generation
            brief = service.generate(
                customer_context=customer_context,
                conversation_context=conversation_context,
                trigger_assessment=trigger_assessment,
                risk_assessment=risk_assessment,
                routing_decision=routing_decision,
                current_sentiment=current_sentiment,
            )

            logger.info(
                "Human brief generated successfully | ticket_id=%s",
                ticket_id,
            )

        except Exception as exc:
            degraded = True
            degradation_reason = str(exc)

            logger.error(
                "Human brief generation failed | ticket_id=%s | error=%s",
                ticket_id,
                str(exc),
            )

    state["human_brief"] = brief

    # 3. Log Telemetry Entry
    log_entry = {
        "node": "brief_generation_node",
        "timestamp": datetime.now(UTC).isoformat(),
        "message": (
            "Fallback human brief used."
            if degraded
            else "Human brief generated successfully."
        ),
        "data": {
            "degraded": degraded,
            "degradation_reason": degradation_reason,
            "assigned_team": (
                routing_decision.assigned_team
                if routing_decision
                else "unknown"
            ),
        },
    }

    state["workflow_logs"].append(log_entry)

    return state