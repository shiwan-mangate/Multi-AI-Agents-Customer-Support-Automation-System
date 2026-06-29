from datetime import datetime, UTC
from typing import Dict, Any
from ..schemas.faq_state import FAQState
from ..services.vector_store import VectorStoreService

import os
from dotenv import load_dotenv, find_dotenv

# Force load, but provide the exact string as a guaranteed fallback
load_dotenv(find_dotenv())
db_url = os.environ.get("FAQ_DATABASE_URL")


def expand_parent_context_node(
    state: FAQState
) -> Dict[str, Any]:
    """
    Implements Parent-Child Small-to-Big retrieval.
    Converts reranked child chunks into full parent FAQ documents
    for grounded answer generation.
    """
    vector_store = VectorStoreService(db_url = db_url)
    now = datetime.now(UTC)
    child_chunks = state.get("reranked_chunks", [])

    
    if not child_chunks:
        reason = "No reranked child chunks available for parent expansion."
        return {
            "current_node": "expand_parent_context_node",
            "updated_at": now,
            "knowledge_gap_detected": True,
            "knowledge_gap_reason": reason,
            "escalation_required": True,
            "escalation_reason": reason,
            "decision_target": "escalation_agent",
            "errors": [reason],
            "workflow_logs": [{
                "timestamp": now.isoformat(),
                "node": "expand_parent_context_node",
                "message": "Parent expansion blocked due to empty child context.",
                "data": {
                    "child_chunk_count": 0
                }
            }]
        }

    try:
        ordered_parent_ids = []

        for chunk in child_chunks:
            parent_id = chunk.get("parent_id")

            if parent_id and parent_id not in ordered_parent_ids:
                ordered_parent_ids.append(parent_id)

        if not ordered_parent_ids:
            reason = "Retrieved child chunks contain no valid parent IDs."

            return {
                "current_node": "expand_parent_context_node",
                "updated_at": now,
                "escalation_required": True,
                "escalation_reason": reason,
                "decision_target": "escalation_agent",
                "errors": [reason]
            }

        parent_contexts = vector_store.get_parent_context(
            ordered_parent_ids
        )

        if not parent_contexts:
            reason = "Parent document lookup returned zero results."

            return {
                "current_node": "expand_parent_context_node",
                "updated_at": now,
                "knowledge_gap_detected": True,
                "knowledge_gap_reason": reason,
                "escalation_required": True,
                "escalation_reason": reason,
                "decision_target": "escalation_agent",
                "errors": [reason]
            }

        
        if len(parent_contexts) != len(ordered_parent_ids):
            reason = "Parent-child integrity mismatch detected."

            return {
                "current_node": "expand_parent_context_node",
                "updated_at": now,
                "escalation_required": True,
                "escalation_reason": reason,
                "decision_target": "escalation_agent",
                "errors": [reason]
            }

        
        parent_map = {
            doc["parent_id"]: doc
            for doc in parent_contexts
        }

        ordered_contexts = [
            parent_map[parent_id]
            for parent_id in ordered_parent_ids
        ]

        return {
            "expanded_parent_context": ordered_contexts,
            "current_node": "expand_parent_context_node",
            "updated_at": now,
            "workflow_logs": [{
                "timestamp": now.isoformat(),
                "node": "expand_parent_context_node",
                "message": (
                    f"Expanded {len(child_chunks)} child chunks "
                    f"into {len(ordered_contexts)} parent documents."
                ),
                "data": {
                    "child_chunk_count": len(child_chunks),
                    "parent_count": len(ordered_contexts)
                }
            }]
        }

    except Exception as e:
        error_msg = f"Parent context expansion failure: {str(e)}"

        return {
            "current_node": "expand_parent_context_node",
            "updated_at": now,
            "escalation_required": True,
            "escalation_reason": error_msg,
            "decision_target": "escalation_agent",
            "errors": [error_msg],
            "workflow_logs": [{
                "timestamp": now.isoformat(),
                "node": "expand_parent_context_node",
                "message": "Database error during parent expansion.",
                "data": {
                    "error": str(e)
                }
            }]
        }