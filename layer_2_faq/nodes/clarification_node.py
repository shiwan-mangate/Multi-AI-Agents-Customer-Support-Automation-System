from datetime import datetime, UTC
from typing import Dict, Any
from langgraph.types import interrupt
from ..schemas.faq_state import FAQState


def clarification_node(state: FAQState) -> Dict[str, Any]:
    """
    HITL clarification pause/resume node.
    """
    now = datetime.now(UTC)
    question = state.get("clarification_question")

    if not question:
        reason = (
            "Clarification node reached without "
            "clarification question."
        )

        return {
            "current_node": "clarification_node",
            "updated_at": now,
            "escalation_required": True,
            "escalation_reason": reason,
            "errors": [reason],
            "workflow_logs": [{
                "timestamp": now.isoformat(),
                "node": "clarification_node",
                "message": reason
            }]
        }

    payload = {
        "type": "clarification_required",
        "question": question,
        "ticket_id": state.get(
            "ticket_id",
            "unknown"
        )
    }

    user_response = interrupt(payload)

    resume_time = datetime.now(UTC)

    if not user_response:
        reason = (
            "User failed to provide clarification."
        )

        return {
            "current_node": "clarification_node",
            "updated_at": resume_time,
            "escalation_required": True,
            "escalation_reason": reason,
            "errors": [reason]
        }

    return {
        "clarification_response": str(
            user_response
        ),
        "clarification_question": None,
        "current_node": "clarification_node",
        "updated_at": resume_time,
        "workflow_logs": [{
            "timestamp": resume_time.isoformat(),
            "node": "clarification_node",
            "message": (
                "Clarification received. "
                "Resuming FAQ workflow."
            ),
            "data": {
                "user_response": str(
                    user_response
                )
            }
        }]
    }