import logging

from layer_3.schemas.translation_record import TranslationRecord
from layer_3.schemas.translation_persistence_event import TranslationPersistenceEvent
from layer_3.repositories.translation_repository import TranslationRepository

logger = logging.getLogger(__name__)

class TranslationPersistenceService:
    """
    The Event Coordinator and Outbound Persistence Manager.
    Packages inbound records into events for future async message brokers (Kafka/SQS)
    and strictly owns the outbound database update lifecycle.
    """

    def __init__(self, repository: TranslationRepository):
        self.repository = repository

    def create_persistence_event(
        self, 
        translation_record: TranslationRecord,
        source_system: str = "inbound_pipeline"
    ) -> TranslationPersistenceEvent:
        """
        Wraps a domain record into an actionable audit event.
        ID and Timestamp generation are delegated to the Pydantic schema.
        """
        logger.info(f"TranslationPersistenceService | Creating Event | Ticket={translation_record.ticket_id}")

        return TranslationPersistenceEvent(
            ticket_id=translation_record.ticket_id,
            customer_id=translation_record.customer_id,
            translation_record=translation_record,
            source_system=source_system,
            processing_status="PENDING"
        )

    def persist_outbound_translation(
        self, 
        ticket_id: str, 
        response_english: str, 
        response_translated: str, 
        response_language: str
    ) -> bool:
        """
        Updates an existing translation record with the agent's outbound response.
        """
        logger.info(f"TranslationPersistenceService | Persisting Outbound | Ticket={ticket_id} | TargetLanguage={response_language}")
        
   
        if not self.repository.translation_exists(ticket_id):
            logger.warning(f"TranslationPersistenceService | Outbound persistence skipped | Ticket={ticket_id} not found in repository.")
            return False
            
        try:
            success = self.repository.update_outbound_translation(
                ticket_id=ticket_id,
                response_english=response_english,
                response_translated=response_translated,
                response_language=response_language
            )

            if success:
                logger.info(f"TranslationPersistenceService | Outbound Persisted Successfully | Ticket={ticket_id}")
            else:
                logger.warning(f"TranslationPersistenceService | Outbound Persistence Failed during update | Ticket={ticket_id}")
            
            return success

        except Exception:
            logger.error(
                f"TranslationPersistenceService | Outbound Persistence Exception | Ticket={ticket_id}", 
                exc_info=True
            )
            return False