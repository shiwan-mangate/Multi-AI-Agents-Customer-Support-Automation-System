# platform_orchestration/adapters/faq_input_adapter.py

from typing import Any

class FAQInputAdapter:
    """Adapts Triage outputs into the strict payload required by your FAQStateFactory."""

    @staticmethod
    def _get_val(obj: Any, key: str, default: Any = None) -> Any:
        """Helper to safely extract data whether obj is a dict or a Pydantic model."""
        if isinstance(obj, dict):
            return obj.get(key, default)
        return getattr(obj, key, default)

    @staticmethod
    def build_payload(triage_output: Any, unified_ticket: Any) -> dict:
        
        # Safely extract the message text depending on what Layer 0 named it
        message_text = (
            FAQInputAdapter._get_val(unified_ticket, "message_text") or 
            FAQInputAdapter._get_val(unified_ticket, "message_raw") or 
            FAQInputAdapter._get_val(unified_ticket, "message", "")
        )

        return {
            "ticket": {
                "ticket_id": FAQInputAdapter._get_val(unified_ticket, "ticket_id"),
                "channel": FAQInputAdapter._get_val(unified_ticket, "channel", "email"),
                "customer_id": FAQInputAdapter._get_val(unified_ticket, "customer_id"),
                "message_raw": message_text, 
                "message_english": message_text,
                "timestamp": FAQInputAdapter._get_val(unified_ticket, "timestamp")
            },
            "ticket_id": FAQInputAdapter._get_val(triage_output, "ticket_id"),
            "customer_id": FAQInputAdapter._get_val(triage_output, "customer_id"),
            "customer_email": FAQInputAdapter._get_val(triage_output, "customer_email", "guest@unknown.com"),
            "next_agent": FAQInputAdapter._get_val(triage_output, "next_agent", "faq_agent"),
            
            "customer_tier": FAQInputAdapter._get_val(triage_output, "customer_tier", "standard"),
            "ltv": FAQInputAdapter._get_val(triage_output, "ltv", 0.0),
            "entities": FAQInputAdapter._get_val(triage_output, "entities", {}),
            "initial_intent": FAQInputAdapter._get_val(triage_output, "initial_intent", "faq"),
            "initial_urgency": FAQInputAdapter._get_val(triage_output, "initial_urgency", "low"),
            "initial_sentiment": FAQInputAdapter._get_val(triage_output, "initial_sentiment", "neutral"),
            "supervisor_confidence": FAQInputAdapter._get_val(triage_output, "supervisor_confidence", 0.0),
            "order_context": FAQInputAdapter._get_val(triage_output, "order_context"),
            "final_priority": FAQInputAdapter._get_val(triage_output, "final_priority", "medium"),
            "sla_duration_hours": FAQInputAdapter._get_val(triage_output, "sla_duration_hours", 24),
            "sla_deadline": FAQInputAdapter._get_val(triage_output, "sla_deadline"),
            
            "escalation_required": False 
        }