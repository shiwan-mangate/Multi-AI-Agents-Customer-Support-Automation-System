from datetime import datetime, UTC
from typing import Dict, Any
import logging

from ..schemas.faq_state import FAQState
from ..services.reranker import RerankerService

logger = logging.getLogger(__name__)

TOP_K = 3


class RerankNode:
    """
    Class-based node for cross-encoder precision reranking.
    Accepts an injected RerankerService to prevent duplicate model loading.
    """
    def __init__(self, reranker_service: RerankerService):
        self.reranker_service = reranker_service

    def __call__(self, state: FAQState) -> Dict[str, Any]:
        now = datetime.now(UTC)

        query = state.get("rewritten_query")
        candidates = state.get(
            "retrieved_child_chunks",
            []
        )

        if not query:
            reason = "Missing rewritten query."

            logger.error(reason)

            return {
                "current_node": "rerank_node",
                "updated_at": now,
                "escalation_required": True,
                "escalation_reason": reason,
                "decision_target": "escalation_agent",
                "errors": [reason],
                "workflow_logs": [{
                    "timestamp": now.isoformat(),
                    "node": "rerank_node",
                    "message": reason
                }]
            }

        if not candidates:
            reason = "No candidate chunks available for reranking."

            logger.warning(reason)

            return {
                "current_node": "rerank_node",
                "updated_at": now,
                "knowledge_gap_detected": True,
                "knowledge_gap_reason": reason,
                "escalation_required": True,
                "escalation_reason": reason,
                "decision_target": "escalation_agent",
                "errors": [reason],
                "workflow_logs": [{
                    "timestamp": now.isoformat(),
                    "node": "rerank_node",
                    "message": reason
                }]
            }

        try:
            # 🟢 FAST EXECUTION: Using the pre-loaded service from RAM
            best_chunks = self.reranker_service.rerank_candidates(
                query=query,
                chunks=candidates,
                top_k=TOP_K
            )

            if not best_chunks:
                reason = "Reranker returned zero usable chunks."

                logger.warning(reason)

                return {
                    "current_node": "rerank_node",
                    "updated_at": now,
                    "knowledge_gap_detected": True,
                    "knowledge_gap_reason": reason,
                    "escalation_required": True,
                    "escalation_reason": reason,
                    "decision_target": "escalation_agent",
                    "errors": [reason]
                }

            rerank_scores = [
                chunk.get("rerank_score", 0.0)
                for chunk in best_chunks
            ]

            return {
                "reranked_chunks": best_chunks,
                "rerank_scores": rerank_scores,
                "current_node": "rerank_node",
                "updated_at": now,
                "workflow_logs": [{
                    "timestamp": now.isoformat(),
                    "node": "rerank_node",
                    "message": (
                        f"Reranked "
                        f"{len(candidates)} candidates "
                        f"to {len(best_chunks)}."
                    ),
                    "data": {
                        "top_score": max(rerank_scores) if rerank_scores else 0.0
                    }
                }]
            }

        except Exception as e:
            error_msg = f"Reranking failure: {str(e)}"

            logger.exception(error_msg)

            return {
                "current_node": "rerank_node",
                "updated_at": now,
                "escalation_required": True,
                "escalation_reason": error_msg,
                "decision_target": "escalation_agent",
                "errors": [error_msg],
                "workflow_logs": [{
                    "timestamp": now.isoformat(),
                    "node": "rerank_node",
                    "message": "Cross-encoder failed.",
                    "data": {
                        "error": str(e)
                    }
                }]
            }