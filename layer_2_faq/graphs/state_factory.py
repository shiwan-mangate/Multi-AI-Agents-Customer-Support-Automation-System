import logging
from datetime import datetime, UTC
from typing import Dict, Any
from ..schemas.faq_state import FAQState

logger = logging.getLogger(__name__)

class FAQStateFactory:
    """
    Production-hardened Entrypoint for the FAQ Specialist Agent.
    Strictly enforces the Triage-to-FAQ contract, preventing silent failures
    and ensuring timezone-aware execution.
    """
    @staticmethod
    def from_triage_payload(payload: Dict[str, Any]) -> FAQState:
        """
        Initializes FAQState from a Triage Agent payload with fail-fast validation.
        """
        FAQStateFactory._validate_payload(payload)
        now = datetime.now(UTC)
    
        sla_deadline_raw = payload.get("sla_deadline")
        if isinstance(sla_deadline_raw, str):
            try:
                sla_deadline = datetime.fromisoformat(sla_deadline_raw)
            except ValueError as e:
                raise ValueError(f"StateFactory: Invalid SLA deadline format: {sla_deadline_raw}") from e
        else:
            sla_deadline = sla_deadline_raw or now

        state: FAQState = {
           
            "ticket": payload["ticket"],
            "entities": payload.get("entities", {}),
            "ticket_id": payload["ticket_id"],
            "customer_email": payload.get("customer_email", "guest@unknown.com"),
            "customer_id": payload["customer_id"],
            "assigned_agent": payload["next_agent"],
            "decision_target": None,

            "initial_intent": payload.get("initial_intent", "faq"),
            "initial_urgency": payload.get("initial_urgency", "medium"),
            "initial_sentiment": payload.get("initial_sentiment", "neutral"),
            "supervisor_confidence": payload.get("supervisor_confidence", 0.0),
            
            "customer_tier": payload.get("customer_tier", "standard"),
            "ltv": payload.get("ltv", 0.0),
            "unresolved_repeat_count": payload.get("unresolved_repeat_count", 0),
            "total_tickets": payload.get("total_tickets", 0),
            "total_escalations": payload.get("total_escalations", 0),
            "last_sentiment": payload.get("last_sentiment", "neutral"),
            
            "order_context": payload.get("order_context"),
            
            # FIX: Enforced lowercase schema constraint for priority fallback
            "final_priority": payload.get("final_priority", "medium"), 
            "sla_duration_hours": payload.get("sla_duration_hours", 24),
            "sla_deadline": sla_deadline,

         
            "rewritten_query": None,
            "query_intent": None,
            "ambiguity_detected": None,
            "clarification_question": None,
            "clarification_response": None,
            "retrieval_strategy": None,
            "metadata_filters": None,

           
            "retrieved_child_chunks": [],
            "similarity_scores": [],
            "reranked_chunks": [],
            "rerank_scores": [],
            "expanded_parent_context": [],

            
            "grounded_answer": None,
            "citations": [],
            "generation_metadata": None,

           
            "verifier_score": None,
            "verifier_reason": None,
            "retry_count": 0,
            "correction_note": None,
            "attempt_history": [],

            "confidence_score": None,

            "feedback_status": "none",
            "feedback_source": None,
            "chunk_quality_updates": [],
            "knowledge_gap_detected": None,
            "knowledge_gap_reason": None,

            "workflow_logs": [],
            "errors": [],
            "timings": {},
            "current_node": "state_factory",
            "created_at": now,
            "updated_at": now,
        }
 
        if state["initial_intent"] != "faq":
            logger.warning(
                f"StateFactory: Intent mismatch. Supervisor said '{state['initial_intent']}', "
                f"but routing to 'faq_agent'. Proceeding with specialist logic."
            )

        state["workflow_logs"].append({
            "timestamp": now.isoformat(),
            "node": "state_factory",
            "message": "FAQ workflow initialized. Contract validated.",
            "data": {
                "ticket_id": state["ticket_id"],
                "intent": state["initial_intent"],
                "tier": state["customer_tier"]
            }
        })

        return state

    @staticmethod
    def _validate_payload(payload: Dict[str, Any]) -> None:
        """Internal validator to enforce business rules and contract safety."""
        
        required_keys = ["ticket", "ticket_id", "customer_id", "next_agent"]
        missing = [key for key in required_keys if key not in payload]
        if missing:
            raise ValueError(f"StateFactory: Missing mandatory triage fields: {missing}")

        ticket = payload["ticket"]
        if not isinstance(ticket, dict) or "message_raw" not in ticket:
            raise ValueError("StateFactory: Ticket object must contain 'message_raw'.")

        if payload.get("escalation_required") is True:
            raise ValueError("StateFactory: Escalated tickets cannot be processed by FAQ Agent.")

        if payload.get("next_agent") != "faq_agent":
            raise ValueError(
                f"StateFactory: Route mismatch. Target must be 'faq_agent', got '{payload['next_agent']}'"
            )