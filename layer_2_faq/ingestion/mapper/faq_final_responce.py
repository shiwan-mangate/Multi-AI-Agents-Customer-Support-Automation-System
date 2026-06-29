# layer_2_faq/ingestion/mapper/faq_final_responce.py

from datetime import datetime, UTC
from layer_2_faq.schemas.faq_output import FAQAgentOutput
from layer_2_faq.schemas.faq_models import Citation
import logging
logger =  logging.getLogger(__name__)

def build_faq_output(final_state) -> FAQAgentOutput:
    """
    Convert LangGraph state -> FAQAgentOutput
    """
    status = "resolved"
    decision_target = final_state.get("decision_target") or "customer"

    if final_state.get("clarification_question"):
        status = "clarification_required"
    elif final_state.get("escalation_required"):
        status = "escalated"
    elif final_state.get("errors"):
        status = "failed"

    # Safely build citations
    raw_citations = final_state.get("citations") or []
    citations = [Citation(**citation) for citation in raw_citations]
    logger.warning(
    "FAQ timings = %s",
    final_state.get("timings")
)
    return FAQAgentOutput(
        # 🟢 FIX: Use .get() with safe fallbacks and explicit type casting
        ticket_id=final_state.get("ticket_id") or "UNKNOWN",
        customer_id=int(final_state.get("customer_id") or 0), 
        
        assigned_agent="faq_agent",
        status=status,
        decision_target=decision_target,
        
        answer=(
            final_state.get("final_answer") or 
            final_state.get("grounded_answer")
        ),
        
        citations=citations,

        confidence_score=float(final_state.get("confidence_score") or 0.0),
        verifier_score=final_state.get("verifier_score"), # Allowed to be None
        
        knowledge_gap_detected=bool(final_state.get("knowledge_gap_detected") or False),
        knowledge_gap_reason=final_state.get("knowledge_gap_reason"),
        
        clarification_question=final_state.get("clarification_question"),
        
        escalation_required=bool(final_state.get("escalation_required") or False),
        escalation_reason=final_state.get("escalation_reason"),
        
        query_intent=final_state.get("query_intent"),
        retrieval_strategy=final_state.get("retrieval_strategy"),
        
        retry_count=int(final_state.get("retry_count") or 0),
        duration_ms=final_state.get("duration_ms"),
        completed_at=datetime.now(UTC)
    )