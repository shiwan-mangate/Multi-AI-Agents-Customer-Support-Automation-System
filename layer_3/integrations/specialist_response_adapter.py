import logging
import json
from typing import Optional, Any

from layer_3.schemas.translation_request import TranslationRequest

from layer_2_faq.schemas.faq_output import FAQAgentOutput
from layer_2_refund.schemas.refund_models import RefundOutput
from layer_2_account_agent.schemas.final_account_agent_responce import AccountAgentResponse
from layer_2_proactive_agent.schemas.proactive_output import ProactiveOutput
from layer_2_escalation_agent.schemas.escalation_output import EscalationAgentResponse

logger = logging.getLogger(__name__)

class SpecialistResponseAdapter:
    """
    Converts Layer 2 specialist outputs into a canonical 
    TranslationRequest consumable by Layer 3.
    """

    def adapt(
        self,
        output: Any,
        target_language: str
    ) -> Optional[TranslationRequest]:

        if isinstance(output, FAQAgentOutput):
            return self.from_faq(output, target_language)

        if isinstance(output, RefundOutput):
            return self.from_refund(output, target_language)

        if isinstance(output, AccountAgentResponse) or (isinstance(output, dict) and "account" in str(output).lower()):
            # 🟢 Catch raw dicts if LangGraph bypassed the Pydantic model during Idempotency
            return self.from_account(output, target_language)

        if isinstance(output, ProactiveOutput):
            return self.from_proactive(output, target_language)

        if isinstance(output, EscalationAgentResponse) or (isinstance(output, dict) and output.get("agent_type") == "escalation_agent"):
            return self.from_escalation(output, target_language)

        # Let's catch generic dicts from resumed workflows just in case
        if isinstance(output, dict) and "ticket_id" in output:
            logger.warning("SpecialistResponseAdapter | Catching untyped dictionary. Attempting generic extraction.")
            return self._generic_dict_extract(output, target_language)

        logger.error(
            f"SpecialistResponseAdapter | UnsupportedOutputType={type(output)}"
        )
        return None

    def _extract_message_defensively(self, obj: Any) -> Optional[str]:
        """Safely extracts message text using a comprehensive list of known keys."""
        if not obj:
            return None
            
        # 🟢 Master list of all possible text fields across all agents
        keys_to_check = [
            "customer_facing_response", # <-- THE MISSING ESCALATION KEY
            "customer_facing_message",
            "resolution",
            "response_message",
            "cached_response",
            "customer_message",
            "customer_response",
            "message",
            "resolution_message",
            "error_message",
            "answer",
            "holding_response",
            "final_response",
            "response_text"
        ]

        # Handle raw dictionaries
        if isinstance(obj, dict):
            for key in keys_to_check:
                val = obj.get(key)
                if val:
                    return str(val)
            return None

        # Handle Pydantic / Class Objects
        for key in keys_to_check:
            val = getattr(obj, key, None)
            if val:
                return str(val)
                
        return None

    def _generic_dict_extract(self, output: dict, target_language: str) -> Optional[TranslationRequest]:
        """Failsafe for raw dictionaries returned by resumed LangGraph workflows."""
        text = self._extract_message_defensively(output)
        if not text:
            return None
            
        return TranslationRequest(
            ticket_id=output.get("ticket_id", "UNKNOWN"),
            source_agent=output.get("agent_type", "unknown_agent"),
            english_response=text,
            target_language=target_language
        )

    def from_faq(self, output: FAQAgentOutput, target_language: str) -> Optional[TranslationRequest]:
        text = None
        status = getattr(output, "status", None)
        
        # 1. Try standard FAQ fields based on status
        if status in ["resolved", "RESOLVED"]:
            text = getattr(output, "answer", None)
        elif status in ["clarification_required", "PENDING_CUSTOMER"]:
            text = getattr(output, "clarification_question", None)
        elif status in ["escalated", "ESCALATED"]:
            text = getattr(output, "escalation_reason", None)

        # 2. Defensive fallback if standard fields were empty
        if not text:
            text = self._extract_message_defensively(output)

        if not text:
            return None

        return TranslationRequest(
            ticket_id=getattr(output, "ticket_id", "UNKNOWN"),
            source_agent="faq_agent",
            english_response=text,
            target_language=target_language
        )

    def from_refund(self, output: RefundOutput, target_language: str) -> Optional[TranslationRequest]:
        text = self._extract_message_defensively(output)
        if not text:
            return None

        return TranslationRequest(
            ticket_id=getattr(output, "ticket_id", "UNKNOWN"),
            source_agent="refund_agent",
            english_response=text,
            target_language=target_language
        )

    def from_account(self, output: Any, target_language: str) -> Optional[TranslationRequest]:
        dump_data = output.model_dump() if hasattr(output, "model_dump") else (vars(output) if hasattr(output, "__dict__") else output)
        text = self._extract_message_defensively(output)
        
        if not text:
            logger.warning("Account Agent Output Dump provided no recognizable text fields.")
            return None

        ticket_id = dump_data.get("ticket_id") if isinstance(dump_data, dict) else getattr(output, "ticket_id", "UNKNOWN")

        return TranslationRequest(
            ticket_id=ticket_id,
            source_agent="account_agent",
            english_response=text,
            target_language=target_language
        )

    def from_proactive(self, output: ProactiveOutput, target_language: str) -> Optional[TranslationRequest]:
        outreach = getattr(output, "outreach_message", None)
        if not outreach:
            return None
            
        text = getattr(outreach, "body", None)
        if not text:
            return None

        return TranslationRequest(
            ticket_id="PROACTIVE",
            correlation_id=getattr(output, "workflow_id", "UNKNOWN"),
            source_agent="proactive_agent",
            english_response=text,
            target_language=target_language
        )

    def from_escalation(self, output: Any, target_language: str) -> Optional[TranslationRequest]:
        # =========================================================
        # 🟢 DEBUG DUMP: Just in case it's missing something else!
        # =========================================================
        dump_data = output.model_dump() if hasattr(output, "model_dump") else (vars(output) if hasattr(output, "__dict__") else output)
        logger.warning("\n" + "="*50)
        logger.warning("🚨 ESCALATION AGENT OUTPUT DUMP 🚨")
        logger.warning(json.dumps(dump_data, indent=2, default=str))
        logger.warning("="*50 + "\n")
        # =========================================================

        if output is None:
            return None

        # Try to extract from the nested 'response' object, fallback to the root object
        resp_obj = getattr(output, "response", None) if not isinstance(output, dict) else dump_data.get("response")

        logger.warning(
        "ESCALATION CUSTOMER MESSAGE = %s",
        getattr(output, "customer_facing_response", None)
    )
        text = self._extract_message_defensively(resp_obj) or self._extract_message_defensively(output)

        if not text:
            logger.warning("EscalationAdapter | Could not find any text fields in the Escalation output!")
            return None

        ticket_id = dump_data.get("ticket_id") if isinstance(dump_data, dict) else getattr(output, "ticket_id", "UNKNOWN")

        return TranslationRequest(
            ticket_id=ticket_id,
            source_agent="escalation_agent",
            english_response=text,
            target_language=target_language
        )