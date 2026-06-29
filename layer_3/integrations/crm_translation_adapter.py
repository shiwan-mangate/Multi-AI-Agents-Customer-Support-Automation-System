import logging
from typing import Dict, Any, Optional
from pydantic import BaseModel

# Assuming Layer 3's TranslationRecord schema
# from layer_3.schemas.translation_record import TranslationRecord

logger = logging.getLogger(__name__)


# 1. OUTBOUND CONTRACT

class CRMTranslationEvent(BaseModel):
    """
    The canonical payload emitted by Layer 3 to the CRM event bus.
    """
    customer_id: int
    ticket_id: str
    customer_language: str
    response_language: str
    customer_original_message: Optional[str] = None
    customer_english_message: Optional[str] = None
    agent_english_response: Optional[str] = None
    agent_translated_response: Optional[str] = None
    translation_success: bool = True



# 2. ADAPTER LOGIC

class CRMTranslationAdapter:
    """
    The final bridge between Layer 3 (Translation) and Layer 4 (CRM Memory).
    Transforms linguistic records into CRM-consumable profile/interaction payloads.
    """

    def from_translation_record(self, record: Any) -> Optional[CRMTranslationEvent]:
        """
        Responsibility 1: Converts a Layer 3 TranslationRecord into a CRMTranslationEvent.
        Note: 'record' typed as Any to decouple from strict SQLAlchemy/Pydantic imports here,
        but expects a TranslationRecord object.
        """
        try:
            # Prevent '0' from evaluating to False
            raw_customer_id = getattr(record, "customer_id", None)
            if raw_customer_id is None:
                logger.error("CRMTranslationAdapter | TranslationRecord missing customer_id.")
                return None
            
            try:
                safe_customer_id = int(raw_customer_id)
            except (ValueError, TypeError):
                logger.error(f"CRMTranslationAdapter | Invalid customer_id format: '{raw_customer_id}'")
                return None

            return CRMTranslationEvent(
                customer_id=safe_customer_id,
                ticket_id=getattr(record, "ticket_id", "UNKNOWN"),
                customer_language=getattr(record, "original_language", "en"),
                response_language=getattr(record, "response_language", "en"),
                customer_original_message=getattr(record, "original_text", None),
                customer_english_message=getattr(record, "english_text", None),
                agent_english_response=getattr(record, "response_english", None),
                agent_translated_response=getattr(record, "response_translated", None),
                translation_success=getattr(record, "translation_success", True)
            )
        except Exception as e:
            logger.error(
                f"CRMTranslationAdapter | Failed to map TranslationRecord to CRM event: {e}", 
                exc_info=True
            )
            return None

    def build_customer_language_update(self, event: CRMTranslationEvent) -> Dict[str, Any]:
        """
        Responsibility 2: Generates the payload to update customer_support_profiles.preferred_language.
        This maps directly to the CRM's CustomerProfile Upsert logic.
        """
        return {
            "customer_id": event.customer_id,
            "preferred_language": event.customer_language,
            "event_source": "layer_3_translation"
        }

    def build_interaction_payload(self, event: CRMTranslationEvent, channel: str = "support_platform") -> Dict[str, Any]:
        """
        Responsibility 3: Generates the payload for CRM interaction history / TranscriptRecord.
        Captures the exact bilingual conversation pairs for the audit ledger.
        """
        return {
            "ticket_id": event.ticket_id,
            "customer_id": event.customer_id,
            "channel": channel,
            "customer_language": event.customer_language,
            "response_language": event.response_language,
            "customer_original_message": event.customer_original_message,
            "customer_english_message": event.customer_english_message,
            "agent_english_response": event.agent_english_response,
            "agent_translated_response": event.agent_translated_response
        }

    def dispatch_to_crm(self, event: CRMTranslationEvent) -> bool:
        """
        Responsibility 4: Transmits the formulated events to the CRM boundary.
        
        TODO (Phase 2): Replace with actual message broker client (KafkaProducer, SQSClient) 
        or CRM Service API HTTP call.
        """
        try:
            language_update = self.build_customer_language_update(event)
            interaction = self.build_interaction_payload(event)

         
            logger.info(
                f"CRMTranslationAdapter | Dispatching event to CRM Event Bus | "
                f"ticket_id={event.ticket_id} | customer_id={event.customer_id}"
            )
            logger.debug(f"CRM Payload - Profile Update: {language_update}")
            logger.debug(f"CRM Payload - Interaction: {interaction}")

            return True

        except Exception as e:
            logger.critical(
                f"CRMTranslationAdapter | CRM Dispatch failed for ticket_id={event.ticket_id}: {e}", 
                exc_info=True
            )
            return False