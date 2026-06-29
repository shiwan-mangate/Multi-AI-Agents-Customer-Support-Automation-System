import logging
from typing import Any, Dict

logger = logging.getLogger(__name__)

class EscalationInputAdapter:
    """
    Adapts Triage outputs and Unified Tickets into the strict payload 
    required by the EscalationStateFactory.
    """

    @staticmethod
    def _get_val(obj: Any, key: str, default: Any = None) -> Any:
        """Safely extract values from either dictionaries or objects."""
        if isinstance(obj, dict):
            return obj.get(key, default)
        return getattr(obj, key, default) if hasattr(obj, key) else default

    def build_payload(
        self, 
        triage_output: Any, 
        unified_ticket: Any, 
        source_agent: str = "triage_agent"
    ) -> Dict[str, Any]:
        """
        Maps orchestration data to the precise payload expected by 
        EscalationStateFactory.from_payload()
        """
        ticket_id = self._get_val(unified_ticket, "ticket_id", "UNKNOWN_TICKET")
        logger.info(f"EscalationInputAdapter mapping ticket: {ticket_id}")

        # 1. Extract Core Ticket Data
        # 🟢 FIX: Check nested "customer" dict since Layer 0 often wraps customer data
        nested_customer = self._get_val(unified_ticket, "customer", {})
        
        raw_customer_id = (
            self._get_val(unified_ticket, "customer_id") or 
            self._get_val(nested_customer, "customer_id", 0)
        )
        
        customer_email = (
            self._get_val(unified_ticket, "customer_email") or 
            self._get_val(nested_customer, "email", "")
        )
        
        channel = self._get_val(unified_ticket, "channel", "email")
        timestamp = self._get_val(unified_ticket, "timestamp", "")
        
        # Safely resolve message payload
        message_raw = (
            self._get_val(unified_ticket, "message_text") or 
            self._get_val(unified_ticket, "message_raw") or 
            self._get_val(unified_ticket, "message", "")
        )
        
        # Fallback to raw if normalized english isn't explicitly passed
        message_english = (
            self._get_val(unified_ticket, "message_english") or 
            message_raw
        )

        # 2. Extract Layer 1 / Triage Context
        # Handle variations in naming conventions between different upstream routers
        initial_intent = self._get_val(triage_output, "intent") or self._get_val(triage_output, "initial_intent", "angry_complex")
        initial_sentiment = self._get_val(triage_output, "sentiment") or self._get_val(triage_output, "initial_sentiment", "neutral")
        initial_urgency = self._get_val(triage_output, "urgency") or self._get_val(triage_output, "initial_urgency", "medium")
        confidence = self._get_val(triage_output, "confidence") or self._get_val(triage_output, "supervisor_confidence", 0.0)
        
        # Ensure entities are ALWAYS a list (EscalationState constraint)
        raw_entities = self._get_val(triage_output, "entities", [])
        entities = raw_entities if isinstance(raw_entities, list) else [raw_entities] if raw_entities else []

        # 🟢 FIX: Safe int conversion (prevents crashes if ID comes in as a weird string or None)
        try:
            customer_id = int(raw_customer_id)
        except (ValueError, TypeError):
            customer_id = 0

        # 3. Construct the Payload Contract
        return {
            "ticket_id": str(ticket_id),
            "customer_id": customer_id,
            "customer_email": str(customer_email),
            "source_agent": source_agent,
            
            # Triage Context
            "initial_intent": str(initial_intent),
            "initial_sentiment": str(initial_sentiment),
            "initial_urgency": str(initial_urgency),
            "supervisor_confidence": float(confidence),
            "entities": entities,
            
            # Initially empty, populated downstream by the conversation_context_node
            "workflow_logs": [], 
            
            # Nested ticket dictionary needed by the state factory
            "ticket": {
                "ticket_id": str(ticket_id),
                "channel": str(channel),
                "customer_id": customer_id,
                "customer_email": str(customer_email),
                "message_raw": str(message_raw),
                "message_english": str(message_english),
                "timestamp": str(timestamp)
            }
        }