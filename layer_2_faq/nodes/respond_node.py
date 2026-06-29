from datetime import datetime, UTC
from typing import Dict, Any
from ..schemas.faq_state import FAQState


def respond_node(state: FAQState) -> Dict[str, Any]:
    """
    Final customer-safe response formatter.
    This node assumes routing has already approved
    delivery to the customer.
    """
    now = datetime.now(UTC)

    grounded_answer = state.get(
        "grounded_answer"
    )

    citations = state.get(
        "citations",
        []
    )

    confidence_score = state.get(
        "confidence_score"
    )

    verifier_score = state.get(
        "verifier_score"
    )

    if not grounded_answer:
        reason = (
            "Respond node reached without "
            "grounded answer."
        )

        return {
            "current_node": "respond_node",
            "updated_at": now,
            "escalation_required": True,
            "escalation_reason": reason,
            "errors": [reason],
            "workflow_logs": [{
                "timestamp": now.isoformat(),
                "node": "respond_node",
                "message": reason
            }]
        }

    success_payload = {
        "status": "success",
        "message": grounded_answer,
        "citations": citations,
        "metadata": {
            "confidence_score": confidence_score,
            "verifier_score": verifier_score
        }
    }

    return {
        "final_response": success_payload,
        "current_node": "respond_node",
        "updated_at": now,
        "workflow_logs": [{
            "timestamp": now.isoformat(),
            "node": "respond_node",
            "message": (
                "Customer response packaged."
            ),
            "data": {
                "citation_count": len(
                    citations
                ),
                "confidence_score": (
                    confidence_score
                )
            }
        }]
    }