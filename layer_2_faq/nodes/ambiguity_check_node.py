from datetime import datetime, UTC
from typing import Dict, Any

from ..schemas.faq_state import FAQState
import logging
logger = logging.getLogger(__name__)

VAGUE_PATTERNS = {
    "help",
    "issue",
    "problem",
    "not working",
    "doesn't work",
    "didn't work",
    "what should i do",
    "fix this",
    "broken",
    "not working properly",
    "this failed",
    "it failed",
    "something went wrong"
}


def ambiguity_check_node(state: FAQState) -> Dict[str, Any]:
    """
    Hybrid ambiguity detection policy.

    Decision sources:
    1. LLM ambiguity classification
    2. Deterministic vague-query detection

    Goals:
    - prevent vague customer messages from silently entering retrieval
    - enforce clarification when required
    - avoid clarification loops after user clarification
    - safely escalate on malformed workflow state
    """
    logger.warning("=" * 60)
    logger.warning("STATE RECEIVED BY AMBIGUITY NODE")
    logger.warning(state)
    logger.warning("=" * 60)
    now = datetime.now(UTC)

    ambiguity_detected = state.get("ambiguity_detected")
    entities = state.get("entities", {})
    ticket = state.get("ticket", {})

    raw_message = str(
        ticket.get("message_raw", "")
    ).lower()

    clarification_response = state.get(
        "clarification_response"
    )

    has_clarification = bool(
        clarification_response
        and str(clarification_response).strip()
    )

    has_useful_entities = any([
        entities.get("order_id"),
        entities.get("product_name"),
        entities.get("subscription_id"),
        entities.get("account_id"),
        entities.get("invoice_id"),
    ])

    if ambiguity_detected is None:
        reason = (
            "Pipeline error: ambiguity_detected is None. "
            "Cannot safely proceed."
        )

        return {
            "current_node": "ambiguity_check_node",
            "updated_at": now,
            "escalation_required": True,
            "escalation_reason": reason,
            "decision_target": "escalation_agent",
            "errors": [reason],
            "workflow_logs": [
                {
                    "timestamp": now.isoformat(),
                    "node": "ambiguity_check_node",
                    "message": "Invalid ambiguity state detected. Escalating.",
                    "data": {
                        "ambiguity_detected": str(
                            ambiguity_detected
                        ),
                        "error": reason,
                    },
                }
            ],
        }

    deterministic_ambiguity = (
        any(
            pattern in raw_message
            for pattern in VAGUE_PATTERNS
        )
        and not has_useful_entities
        and not has_clarification
    )

    final_ambiguity = (
        ambiguity_detected is True
        or deterministic_ambiguity
    )

    if not final_ambiguity:
        return {
            "current_node": "ambiguity_check_node",
            "updated_at": now,
            "clarification_question": None,
            "workflow_logs": [
                {
                    "timestamp": now.isoformat(),
                    "node": "ambiguity_check_node",
                    "message": (
                        "Query intent is clear. "
                        "Proceeding to retrieval strategy."
                    ),
                    "data": {
                        "llm_ambiguity": ambiguity_detected,
                        "deterministic_ambiguity": deterministic_ambiguity,
                        "has_clarification": has_clarification,
                        "clarification_required": False,
                    },
                }
            ],
        }

    order_id = entities.get("order_id")
    product_name = entities.get("product_name")
    subscription_id = entities.get("subscription_id")
    account_id = entities.get("account_id")

    if not order_id and product_name:
        question = (
            "Could you tell me which order you're referring to "
            "so I can help accurately?"
        )

    elif order_id and not product_name:
        question = (
            "Which specific product are you asking about?"
        )

    elif subscription_id:
        question = (
            "Could you clarify what issue you're facing with "
            "your subscription?"
        )

    elif account_id:
        question = (
            "Could you describe the account issue you're experiencing?"
        )

    else:
        question = (
            "Could you please clarify what specific product, "
            "service, or issue you're referring to so I can help accurately?"
        )

    return {
        "current_node": "ambiguity_check_node",
        "updated_at": now,
        "clarification_question": question,
        "decision_target": "clarification_node",
        "workflow_logs": [
            {
                "timestamp": now.isoformat(),
                "node": "ambiguity_check_node",
                "message": "Ambiguity detected. Clarification required.",
                "data": {
                    "llm_ambiguity": ambiguity_detected,
                    "deterministic_ambiguity": deterministic_ambiguity,
                    "has_clarification": has_clarification,
                    "clarification_required": True,
                    "question_generated": question,
                },
            }
        ],
    }