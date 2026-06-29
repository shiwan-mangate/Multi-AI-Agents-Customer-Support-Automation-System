import logging
from typing import Literal

from ..schemas.faq_state import FAQState

logger = logging.getLogger(__name__)


def route_after_validation(
    state: FAQState
) -> Literal["escalation_handoff_node", "query_understanding_node"]:

    logger.info(
        f"[VALIDATION ROUTER] escalation_required="
        f"{state.get('escalation_required')}"
    )

    if state.get("escalation_required"):
        logger.warning(
            "[VALIDATION ROUTER] Routing to escalation_handoff_node."
        )
        return "escalation_handoff_node"

    logger.info(
        "[VALIDATION ROUTER] Routing to query_understanding_node."
    )
    return "query_understanding_node"


def route_after_ambiguity(
    state: FAQState
) -> Literal[
    "clarification_node",
    "escalation_handoff_node",
    "retrieval_strategy_node"
]:

    logger.info(
        f"[AMBIGUITY ROUTER] "
        f"escalation_required={state.get('escalation_required')} "
        f"clarification_question="
        f"{bool(state.get('clarification_question'))}"
    )

    if state.get("escalation_required"):
        logger.warning(
            "[AMBIGUITY ROUTER] Routing to escalation_handoff_node."
        )
        return "escalation_handoff_node"

    if state.get("clarification_question"):
        logger.info(
            "[AMBIGUITY ROUTER] Routing to clarification_node."
        )
        return "clarification_node"

    logger.info(
        "[AMBIGUITY ROUTER] Routing to retrieval_strategy_node."
    )
    return "retrieval_strategy_node"


def route_after_confidence(
    state: FAQState
) -> Literal[
    "respond_node",
    "query_understanding_node",
    "escalation_handoff_node"
]:

    target = state.get("decision_target")
    retry_count = state.get("retry_count", 0)
    knowledge_gap = state.get("knowledge_gap_detected", False)
    confidence_score = state.get("confidence_score")
    verifier_score = state.get("verifier_score")

    logger.info(
        "[CONFIDENCE ROUTER] "
        f"target={target} | "
        f"retry_count={retry_count} | "
        f"knowledge_gap={knowledge_gap} | "
        f"confidence_score={confidence_score} | "
        f"verifier_score={verifier_score}"
    )

    # Success path
    if target == "customer":
        logger.info(
            "[CONFIDENCE ROUTER] "
            "Routing to respond_node."
        )
        return "respond_node"

    # Escalation path
    if target == "escalation_agent":

        if knowledge_gap:
            logger.warning(
                "[CONFIDENCE ROUTER] "
                "Hard knowledge gap detected. "
                "Routing to escalation_handoff_node."
            )
            return "escalation_handoff_node"

        if retry_count < 2:
            logger.info(
                "[CONFIDENCE ROUTER] "
                f"Low confidence retry. "
                f"Current retry_count={retry_count}. "
                f"Routing back to query_understanding_node."
            )
            return "query_understanding_node"

        logger.warning(
            "[CONFIDENCE ROUTER] "
            f"Max retries exhausted "
            f"(retry_count={retry_count}). "
            "Routing to escalation_handoff_node."
        )
        return "escalation_handoff_node"

    logger.error(
        "[CONFIDENCE ROUTER] "
        f"Unknown decision_target={target}. "
        "Routing to escalation_handoff_node."
    )

    return "escalation_handoff_node"