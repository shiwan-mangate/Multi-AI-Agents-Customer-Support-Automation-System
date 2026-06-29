from datetime import datetime, UTC
from typing import Dict, Any

from ..schemas.faq_state import FAQState
from ..services.verifier import VerifyAnswerService
from layer_2_faq.llm import create_llm
llm = create_llm()

verifier_service = VerifyAnswerService()

def verify_answer_node(
    state: FAQState
) -> Dict[str, Any]:
    """
    Critic verification layer.
    Evaluates grounded answer quality and feeds the
    confidence gate for retry/escalation decisions.
    """
    now = datetime.now(UTC)

    query = state.get("rewritten_query")
    grounded_answer = state.get("grounded_answer")
    citations = state.get("citations", [])
    parent_contexts = state.get(
        "expanded_parent_context",
        []
    )


    if state.get("knowledge_gap_detected"):
        return {
            "verifier_score": 1.0,
            "verifier_reason": (
                "Knowledge gap correctly detected."
            ),
            "current_node": "verify_answer_node",
            "updated_at": now,
            "workflow_logs": [{
                "timestamp": now.isoformat(),
                "node": "verify_answer_node",
                "message": (
                    "Verification skipped due to "
                    "knowledge gap."
                )
            }]
        }

    try:
        verification_result = (
            verifier_service.verify(
                query=query,
                grounded_answer=grounded_answer,
                citations=citations,
                parent_contexts=parent_contexts
            )
        )

        correction_note = None

        if verification_result.verdict == "fail":
            correction_note = (
                verification_result.failure_reason
            )

        return {
            "verifier_score": (
                verification_result.verifier_score
            ),
            "verifier_reason": (
                verification_result.failure_reason
            ),
            "correction_note": correction_note,
            "current_node": "verify_answer_node",
            "updated_at": now,
            "workflow_logs": [{
                "timestamp": now.isoformat(),
                "node": "verify_answer_node",
                "message": "Answer verification complete.",
                "data": {
                    "score": (
                        verification_result.verifier_score
                    ),
                    "verdict": (
                        verification_result.verdict
                    )
                }
            }]
        }

    except Exception as e:
        error_msg = (
            f"Verifier node failure: {str(e)}"
        )

        return {
            "verifier_score": 0.0,
            "verifier_reason": error_msg,
            "correction_note": error_msg,
            "current_node": "verify_answer_node",
            "updated_at": now,
            "workflow_logs": [{
                "timestamp": now.isoformat(),
                "node": "verify_answer_node",
                "message": "Verifier execution failed.",
                "data": {
                    "error": str(e)
                }
            }]
        }