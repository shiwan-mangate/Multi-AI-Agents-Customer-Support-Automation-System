import logging

from layer_3.schemas.bilingual_message import BilingualMessage
from layer_3.schemas.translation_persistence_event import TranslationPersistenceEvent
from layer_3.storage.bilingual_store_service import BilingualStoreService
from layer_3.storage.translation_persistence_service import TranslationPersistenceService

logger = logging.getLogger(__name__)

class BackgroundTasksService:
    """
    Coordinator for asynchronous/deferred operations within Layer 3.
    Ensures that database writes and event dispatching do not block 
    immediate response returns to Layer 1 (Supervisor) or Layer 2 (Agents).
    """

    def __init__(
        self, 
        store_service: BilingualStoreService, 
        persistence_service: TranslationPersistenceService
    ):
        self.store_service = store_service
        self.persistence_service = persistence_service

    def persist_inbound_translation(
        self, 
        ticket_id: str, 
        customer_id: int, 
        bilingual_message: BilingualMessage
    ) -> bool:
        """
        Deferred execution: Stores the inbound translation, generates an event, 
        and dispatches it. Returns True if fully successful.
        """
        logger.info(f"BackgroundTasksService | Starting async inbound persistence | Ticket={ticket_id}")
        
        try:
            # 1. Transform and Persist
            record = self.store_service.store_inbound_message(
                ticket_id=ticket_id,
                customer_id=customer_id,
                bilingual_message=bilingual_message
            )
            
            # 2. Wrap in Persistence Event
            event = self.persistence_service.create_persistence_event(
                translation_record=record
            )
            
            # 3. Dispatch to Message Broker
            return self.dispatch_translation_event(event)
            
        except Exception:
            logger.error(
                f"BackgroundTasksService | Inbound persistence failed | Ticket={ticket_id}", 
                exc_info=True
            )
            return False

    def persist_outbound_translation(
        self, 
        ticket_id: str, 
        response_english: str, 
        response_translated: str, 
        response_language: str
    ) -> bool:
        """
        Deferred execution: Updates an existing translation record with the agent's 
        outbound response. Returns True if the database updated successfully.
        """
        logger.info(f"BackgroundTasksService | Starting async outbound persistence | Ticket={ticket_id}")
        
        try:
            success = self.persistence_service.persist_outbound_translation(
                ticket_id=ticket_id,
                response_english=response_english,
                response_translated=response_translated,
                response_language=response_language
            )
            return success
        except Exception:
            logger.error(
                f"BackgroundTasksService | Outbound persistence failed | Ticket={ticket_id}", 
                exc_info=True
            )
            return False

    def dispatch_translation_event(self, event: TranslationPersistenceEvent) -> bool:
        """
        Simulates dispatching an event to a Kafka/SQS topic for downstream consumption.
        """
        logger.info(f"BackgroundTasksService | Dispatching event | EventID={event.event_id} | Ticket={event.ticket_id}")
        
        try:
            # MVP: Log the payload natively using Pydantic v2
            logger.info(
                f"MESSAGE BROKER DISPATCH -> "
                f"Topic: translation.inbound.processed | "
                f"Payload: {event.model_dump_json()}"
            )
            return True
        except Exception:
            logger.error(
                f"BackgroundTasksService | Event dispatch failed | EventID={event.event_id}", 
                exc_info=True
            )
            return False