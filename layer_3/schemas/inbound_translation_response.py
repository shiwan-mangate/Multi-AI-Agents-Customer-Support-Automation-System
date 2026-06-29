from pydantic import BaseModel
from layer_3.schemas.bilingual_message import BilingualMessage
from layer_3.schemas.translation_record import TranslationRecord
from layer_3.schemas.translation_persistence_event import TranslationPersistenceEvent

class InboundTranslationResponse(BaseModel):
    """
    Strict domain contract returned to Layer 1 (Supervisor) 
    after processing an inbound customer message.
    """
    bilingual_message: BilingualMessage
    translation_record: TranslationRecord
    persistence_event: TranslationPersistenceEvent