from datetime import datetime, UTC
from typing import Dict, Any

from ..schemas.faq_state import FAQState
from ..services.answer_generator import AnswerGeneratorService
from layer_2_faq.llm import create_llm
llm = create_llm()
generator_service = AnswerGeneratorService(llm=llm)


def generate_answer_node(
    state: FAQState
) -> Dict[str, Any]:
    """
    Grounded answer synthesis node.
    """
    now = datetime.now(UTC)

    query = state.get("rewritten_query")
    parent_contexts = state.get(
        "expanded_parent_context",
        []
    )

    if not query:
        reason = "Missing rewritten query."

        return {
            "current_node": "generate_answer_node",
            "updated_at": now,
            "escalation_required": True,
            "escalation_reason": reason,
            "decision_target": "escalation_agent",
            "errors": [reason]
        }

    if not parent_contexts:
        reason = "Missing parent KB context."

        return {
            "current_node": "generate_answer_node",
            "updated_at": now,
            "knowledge_gap_detected": True,
            "knowledge_gap_reason": reason,
            "escalation_required": True,
            "escalation_reason": reason,
            "decision_target": "escalation_agent",
            "errors": [reason]
        }

    crm_context = {
        "customer_tier": state.get("customer_tier"),
        "ltv": state.get("ltv"),
        "unresolved_repeat_count": state.get(
            "unresolved_repeat_count"
        ),
        "total_escalations": state.get(
            "total_escalations"
        ),
        "last_sentiment": state.get(
            "last_sentiment"
        ),
        "order_context": state.get("order_context"),
        "retry_count": state.get("retry_count", 0)
    }

    try:
        result = generator_service.generate(
            query=query,
            parent_contexts=parent_contexts,
            crm_data=crm_context
        )

        citations_dump = [
            c.model_dump()
            for c in result.citations
        ]

        return {
            "grounded_answer": result.grounded_answer,
            "citations": citations_dump,
            "knowledge_gap_detected": result.knowledge_gap,
            "knowledge_gap_reason": (
                "LLM determined context lacks answer."
                if result.knowledge_gap
                else None
            ),
            "generation_metadata": {
                "context_count": len(parent_contexts),
                "citation_count": len(citations_dump),
                "knowledge_gap": result.knowledge_gap,
                "model": "llama-3.3-70b-versatile"
            },
            "current_node": "generate_answer_node",
            "updated_at": now,
            "workflow_logs": [{
                "timestamp": now.isoformat(),
                "node": "generate_answer_node",
                "message": "Structured grounded generation complete.",
                "data": {
                    "knowledge_gap": result.knowledge_gap,
                    "citation_count": len(citations_dump)
                }
            }]
        }

    except Exception as e:
        error_msg = f"Generation failure: {str(e)}"

        return {
            "current_node": "generate_answer_node",
            "updated_at": now,
            "escalation_required": True,
            "escalation_reason": error_msg,
            "decision_target": "escalation_agent",
            "errors": [error_msg],
            "workflow_logs": [{
                "timestamp": now.isoformat(),
                "node": "generate_answer_node",
                "message": "Answer generation failed.",
                "data": {
                    "error": str(e)
                }
            }]
        }