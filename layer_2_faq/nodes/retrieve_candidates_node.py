from datetime import datetime, UTC
from typing import Dict, Any
import logging

from ..schemas.faq_state import FAQState
from ..schemas.faq_models import RetrievedChunk
from ..services.vector_store import VectorStoreService

logger = logging.getLogger(__name__)

TOP_K = 10

class RetrieveCandidatesNode:
    """
    Class-based node for executing semantic retrieval against pgvector.
    Accepts an injected VectorStoreService to prevent duplicate model loading and DB connections.
    """
    def __init__(self, vector_store: VectorStoreService):
        # Store the pre-loaded service passed from the container
        self.vector_store = vector_store

    def __call__(self, state: FAQState) -> Dict[str, Any]:
        """LangGraph will call this method when the node executes."""
        now = datetime.now(UTC)

        query = state.get("rewritten_query")
        filters = state.get("metadata_filters", {})

        if not query:
            reason = "Missing rewritten_query in FAQ state."
            logger.error(reason)

            return {
                "current_node": "retrieve_candidates_node",
                "updated_at": now,
                "escalation_required": True,
                "escalation_reason": reason,
                "decision_target": "escalation_agent",
                "errors": [reason],
                "workflow_logs": [{
                    "timestamp": now.isoformat(),
                    "node": "retrieve_candidates_node",
                    "message": "Retrieval aborted due to invalid state.",
                    "data": {"reason": reason}
                }]
            }

        try:
            # 🟢 FAST EXECUTION: Using the pre-connected database service!
            raw_results = self.vector_store.search_candidates(
                query=query,
                filters=filters,
                top_k=TOP_K
            )
            for result in raw_results:
                logger.warning(
                f"RETRIEVED | "
                f"chunk={result['chunk_id']} | "
                f"category={result['category']} | "
                f"similarity={result['similarity_score']}"
            )

            if not raw_results:
                reason = "Semantic retrieval returned zero matches."
                logger.warning(reason)

                return {
                    "current_node": "retrieve_candidates_node",
                    "updated_at": now,
                    "knowledge_gap_detected": True,
                    "knowledge_gap_reason": reason,
                    "escalation_required": True,
                    "escalation_reason": reason,
                    "decision_target": "escalation_agent",
                    "errors": [reason],
                    "workflow_logs": [{
                        "timestamp": now.isoformat(),
                        "node": "retrieve_candidates_node",
                        "message": "Knowledge gap detected during semantic retrieval.",
                        "data": {
                            "query": query,
                            "filters": filters
                        }
                    }]
                }

            validated_chunks = []

            for result in raw_results:
                chunk = RetrievedChunk(
                    chunk_id=result["chunk_id"],
                    parent_id=result["parent_id"],
                    content=result["content"],
                    similarity_score=result["similarity_score"],
                    metadata={
                        "document_name": result["document_name"],
                        "section": result.get("section"),
                        "category": result["category"]
                    }
                )

                validated_chunks.append(chunk.model_dump())

            similarity_scores = [
                chunk["similarity_score"]
                for chunk in validated_chunks
                if chunk.get("similarity_score") is not None
            ]

            return {
                "retrieved_child_chunks": validated_chunks,
                "similarity_scores": similarity_scores,
                "current_node": "retrieve_candidates_node",
                "updated_at": now,
                "workflow_logs": [{
                    "timestamp": now.isoformat(),
                    "node": "retrieve_candidates_node",
                    "message": (
                        f"Semantic retrieval succeeded with "
                        f"{len(validated_chunks)} candidate chunks."
                    ),
                    "data": {
                        "count": len(validated_chunks)
                    }
                }]
            }

        except Exception as e:
            error_msg = f"Vector retrieval failure: {str(e)}"
            logger.exception(error_msg)

            return {
                "current_node": "retrieve_candidates_node",
                "updated_at": now,
                "escalation_required": True,
                "escalation_reason": error_msg,
                "decision_target": "escalation_agent",
                "errors": [error_msg],
                "workflow_logs": [{
                    "timestamp": now.isoformat(),
                    "node": "retrieve_candidates_node",
                    "message": "Semantic retrieval failed.",
                    "data": {
                        "error": str(e)
                    }
                }]
            }