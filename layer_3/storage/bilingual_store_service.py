import logging

from layer_3.schemas.bilingual_message import BilingualMessage
from layer_3.schemas.translation_record import TranslationRecord
from layer_3.repositories.translation_repository import TranslationRepository

logger = logging.getLogger(__name__)

class BilingualStoreService:
    """
    Transforms and persists inbound translations.
    Acts as the strict boundary between the Inbound Pipeline (Domain Logic) 
    and the Translation Repository (Data Access).
    """

    def __init__(self, repository: TranslationRepository):
        self.repository = repository

    def store_inbound_message(
        self, 
        ticket_id: str, 
        customer_id: int, 
        bilingual_message: BilingualMessage
    ) -> TranslationRecord:
        """
        Converts a pipeline BilingualMessage into a persistence TranslationRecord
        and coordinates its storage safely with idempotency checks.
        """
        logger.info(f"BilingualStoreService | Storing inbound message | Ticket={ticket_id} | Customer={customer_id}")

      
        translation_success = not bilingual_message.language_context.translation_failed

       
        record = TranslationRecord(
            ticket_id=ticket_id,
            customer_id=customer_id, 
            original_text=bilingual_message.original_text,
            original_language=bilingual_message.language_context.detected_language,
            english_text=bilingual_message.english_text,
            translation_service="helsinki",
            translation_success=translation_success
        )

    
        if self.repository.translation_exists(ticket_id):
            logger.warning(f"BilingualStoreService | Translation already exists | Ticket={ticket_id}")
            return record

   
        try:
            self.repository.create_record(record)
            logger.info(f"BilingualStoreService | Successfully stored record | Ticket={ticket_id}")
        except Exception:
            logger.error(
                f"BilingualStoreService | Failed to store record | Ticket={ticket_id}", 
                exc_info=True
            )
            raise

   
        return record