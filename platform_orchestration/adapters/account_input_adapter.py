# platform_orchestration/adapters/account_input_adapter.py

from typing import Any

class AccountInputAdapter:
    """Adapts Triage outputs into the strict payload required by the AccountStateFactory."""

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
            AccountInputAdapter._get_val(unified_ticket, "message_text") or 
            AccountInputAdapter._get_val(unified_ticket, "message_raw") or 
            AccountInputAdapter._get_val(unified_ticket, "message", "")
        )

        return {
            # ---------- Base Ticket Info ----------
            "ticket": {
                "ticket_id": AccountInputAdapter._get_val(unified_ticket, "ticket_id"),
                "channel": AccountInputAdapter._get_val(unified_ticket, "channel", "email"),
                "customer_id": AccountInputAdapter._get_val(unified_ticket, "customer_id"),
                "message_raw": message_text, 
                "message_english": message_text,
                "timestamp": AccountInputAdapter._get_val(unified_ticket, "timestamp")
            },
            "ticket_id": AccountInputAdapter._get_val(triage_output, "ticket_id", "UNKNOWN"),
            "customer_id": AccountInputAdapter._get_val(triage_output, "customer_id"),
            "customer_email": AccountInputAdapter._get_val(triage_output, "customer_email", "guest@unknown.com"),
            "next_agent": AccountInputAdapter._get_val(triage_output, "next_agent", "account_agent"),
            
            # ---------- Context & Analytics ----------
            "customer_tier": AccountInputAdapter._get_val(triage_output, "customer_tier", "standard"),
            "ltv": float(AccountInputAdapter._get_val(triage_output, "ltv") or 0.0),
            "entities": AccountInputAdapter._get_val(triage_output, "entities", {}),
            
            # ---------- Classification ----------
            "initial_intent": AccountInputAdapter._get_val(triage_output, "initial_intent", "account_issue"),
            "initial_urgency": AccountInputAdapter._get_val(triage_output, "initial_urgency", "medium"),
            "initial_sentiment": AccountInputAdapter._get_val(triage_output, "initial_sentiment", "neutral"),
            "supervisor_confidence": float(AccountInputAdapter._get_val(triage_output, "supervisor_confidence") or 0.0),
            
            # ---------- Account Specific Metrics ----------
            "unresolved_repeat_count": int(AccountInputAdapter._get_val(triage_output, "unresolved_repeat_count") or 0),
            "total_tickets": int(AccountInputAdapter._get_val(triage_output, "total_tickets") or 1),
            "total_escalations": int(AccountInputAdapter._get_val(triage_output, "total_escalations") or 0),
            
            # ---------- SLA & Priority ----------
            "final_priority": AccountInputAdapter._get_val(triage_output, "final_priority", "medium"),
            "sla_duration_hours": int(AccountInputAdapter._get_val(triage_output, "sla_duration_hours") or 24),
            "sla_deadline": AccountInputAdapter._get_val(triage_output, "sla_deadline"),
            
            # ---------- Workflow Control ----------
            "clarification_required": False
        }