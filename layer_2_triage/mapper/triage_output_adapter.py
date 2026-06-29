from datetime import datetime, timezone
from layer_2_triage.graphs.triage_state import TriageState
from layer_2_triage.schemas.triage_output import TriageOutput

def build_triage_output(state: TriageState) -> TriageOutput:
    """
    Serializer: Maps the complex internal TriageState to a 
    clean, external-facing TriageOutput schema.
    """
    return {
        "ticket_id": state["ticket_id"],
        "customer_id": state["customer_id"],
        "customer_email": state["customer_email"],
        "customer_tier": state["customer_tier"],
        "ltv": state["ltv"],
        "initial_intent": state["initial_intent"],
        "initial_urgency": state["initial_urgency"],
        "initial_sentiment": state["initial_sentiment"],
        "supervisor_confidence": state["supervisor_confidence"],
        "entities": state["entities"],
        "order_context": state.get("order_context"),
        "final_score": state["final_score"],
        "final_priority": state["final_priority"],
        "sla_duration_hours": state["sla_duration_hours"],
        "sla_deadline": state["sla_deadline"],
        "escalation_required": state["escalation_required"],
        "escalation_reason": state["escalation_reason"],
        "insight_tags": state["insight_tags"],
        "next_agent": state["next_agent"],
        # Updated to timezone-aware UTC for future-proofing
        "triage_completed_at": datetime.now(timezone.utc)
    }