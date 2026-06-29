import logging
from typing import Dict, Any, Optional

from layer_3.repositories.translation_repository import TranslationRepository

from layer_3.pipeline.inbound_translation_pipeline import InboundTranslationPipeline
from layer_3.pipeline.outbound_translation_pipeline import OutboundTranslationPipeline

from layer_3.storage.bilingual_store_service import BilingualStoreService
from layer_3.storage.translation_persistence_service import TranslationPersistenceService
from layer_3.storage.translation_analytics_service import TranslationAnalyticsService

from layer_3.schemas.inbound_translation_response import InboundTranslationResponse
from layer_3.schemas.translation_result import TranslationResult

logger = logging.getLogger(__name__)

class TranslationService:
    """
    Master Facade for Layer 3 (Translation Subsystem).
    Orchestrates detection, protection, translation, and storage without exposing 
    underlying complexities to the Supervisor or Specialist Agents.
    """

    def __init__(self, repository: TranslationRepository):
       
        self.repository = repository
      
        self.inbound_pipeline = InboundTranslationPipeline()
        self.outbound_pipeline = OutboundTranslationPipeline()

        self.store_service = BilingualStoreService(self.repository)
        self.persistence_service = TranslationPersistenceService(self.repository)
        self.analytics_service = TranslationAnalyticsService(self.repository)

    def process_inbound_message(
        self, 
        ticket_id: str, 
        customer_id: int, 
        message: str, 
        customer_context: Optional[Dict[str, Any]] = None
    ) -> InboundTranslationResponse:
        """
        Orchestrates the inbound flow: Translation -> Persistence -> Event Generation.
        """
        logger.info(f"TranslationService | Processing Inbound | Ticket={ticket_id} | Customer={customer_id}")

        try:
         
            bilingual_message = self.inbound_pipeline.process_inbound(
                text=message, 
                customer_context=customer_context
            )

        
            translation_record = self.store_service.store_inbound_message(
                ticket_id=ticket_id,
                customer_id=customer_id,
                bilingual_message=bilingual_message
            )

           
            persistence_event = self.persistence_service.create_persistence_event(
                translation_record=translation_record
            )

            logger.info(
                f"TranslationService | Inbound Complete | "
                f"Ticket={ticket_id} | Language={bilingual_message.language_context.detected_language}"
            )

           
            return InboundTranslationResponse(
                bilingual_message=bilingual_message,
                translation_record=translation_record,
                persistence_event=persistence_event
            )

        except Exception:
            logger.error(f"TranslationService | Inbound Exception | Ticket={ticket_id}", exc_info=True)
            raise

    def process_outbound_response(
        self, 
        ticket_id: str, 
        english_response: str, 
        target_language: str, 
        source_agent: Optional[str] = None
    ) -> TranslationResult:
        """
        Orchestrates the outbound flow: Translation -> Database Update -> Result Return.
        """
        logger.info(f"TranslationService | Processing Outbound | Ticket={ticket_id} | Target={target_language}")

        try:
          
            translation_result = self.outbound_pipeline.process_outbound(
                english_response=english_response,
                target_language=target_language,
                source_agent=source_agent
            )

         
            if translation_result.translation_success:
                self.persistence_service.persist_outbound_translation(
                    ticket_id=ticket_id,
                    response_english=english_response,
                    response_translated=translation_result.translated_text,
                    response_language=target_language
                )
            else:
                logger.warning(
                    f"TranslationService | Outbound Persistence Skipped | "
                    f"Ticket={ticket_id} | Reason=TranslationFailed"
                )

            logger.info(
                f"TranslationService | Outbound Complete | "
                f"Ticket={ticket_id} | Target={target_language} | Success={translation_result.translation_success}"
            )

        
            return translation_result

        except Exception:
            logger.error(f"TranslationService | Outbound Exception | Ticket={ticket_id}", exc_info=True)
            raise

    def get_customer_language_profile(self, customer_id: int) -> Dict[str, Any]:
        """
        Convenience method exposing language analytics for the ContextSignalResolver.
        """
        return self.analytics_service.get_customer_language_profile(customer_id)