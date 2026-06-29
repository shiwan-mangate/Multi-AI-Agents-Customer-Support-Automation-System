from datetime import datetime, UTC
from typing import Dict, Any
from ..schemas.faq_state import FAQState

import logging

logger = logging.getLogger(__name__)

WEIGHT_SIMILARITY = 0.15
WEIGHT_RERANK = 0.35
WEIGHT_VERIFIER = 0.50

CONFIDENCE_THRESHOLD = 0.75


def _clip(
    value: float,
    minimum: float = 0.0,
    maximum: float = 1.0
) -> float:
    return max(minimum, min(value, maximum))


def confidence_gate_node(
    state: FAQState
) -> Dict[str, Any]:
    now = datetime.now(UTC)

    if (
        state.get("knowledge_gap_detected")
        or state.get("escalation_required")
    ):
        return {
            "confidence_score": 0.0,
            "decision_target": "escalation_agent",
            "current_node": "confidence_gate_node",
            "updated_at": now,
            "workflow_logs": [{
                "timestamp": now.isoformat(),
                "node": "confidence_gate_node",
                "message": (
                    "Hard failure detected. "
                    "Confidence forced to zero."
                )
            }]
        }

    similarity_scores = state.get(
        "similarity_scores",
        []
    )

    rerank_scores = state.get(
        "rerank_scores",
        []
    )

    verifier_score = state.get(
        "verifier_score"
    )

    if verifier_score is None:
        reason = "Missing verifier score."

        return {
            "confidence_score": 0.0,
            "decision_target": "escalation_agent",
            "verifier_reason": reason,
            "current_node": "confidence_gate_node",
            "updated_at": now,
            "workflow_logs": [{
                "timestamp": now.isoformat(),
                "node": "confidence_gate_node",
                "message": reason
            }]
        }

    max_similarity = _clip(
        float(max(similarity_scores))
        if similarity_scores
        else 0.0
    )

    max_rerank = _clip(
        float(max(rerank_scores))
        if rerank_scores
        else 0.0
    )

    verifier_score = _clip(
        float(verifier_score)
    )

    confidence = round(
        (max_similarity * WEIGHT_SIMILARITY)
        + (max_rerank * WEIGHT_RERANK)
        + (verifier_score * WEIGHT_VERIFIER),
        3
    )

    current_retry = state.get("retry_count", 0)

    if verifier_score >= 0.85:
        decision_target = "customer"
    else:
        decision_target = (
            "customer"
            if confidence >= CONFIDENCE_THRESHOLD
            else "escalation_agent"
        )

    updated_retry_count = current_retry

    # Increment retry counter only for low-confidence retries
    if (
        decision_target == "escalation_agent"
        and not state.get("knowledge_gap_detected", False)
    ):
        updated_retry_count += 1

    logger.info(
    "CONFIDENCE COMPONENTS | "
    f"similarity={max_similarity:.3f} | "
    f"rerank={max_rerank:.3f} | "
    f"verifier={verifier_score:.3f} | "
    f"final={confidence:.3f} | "
    f"target={decision_target}"
)

    return {
        "confidence_score": confidence,
        "decision_target": decision_target,
        "retry_count": updated_retry_count,
        "current_node": "confidence_gate_node",
        "updated_at": now,
        "workflow_logs": [{
            "timestamp": now.isoformat(),
            "node": "confidence_gate_node",
            "message": "Confidence score computed.",
            "data": {
                "confidence_score": confidence,
                "decision_target": decision_target,
                "threshold": CONFIDENCE_THRESHOLD,
                "retry_count_before": current_retry,
                "retry_count_after": updated_retry_count,
                "max_similarity": max_similarity,
                "max_rerank": max_rerank,
                "verifier_score": verifier_score
            }
        }]
    }