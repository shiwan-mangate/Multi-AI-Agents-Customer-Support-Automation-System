import uuid
from datetime import datetime, timezone
from pydantic import BaseModel, Field

from layer_3.schemas.translation_record import TranslationRecord

def generate_event_id() -> str:
    return f"evt_{uuid.uuid4().hex[:16]}"

def generate_utc_now() -> datetime:
    return datetime.now(timezone.utc)

class TranslationPersistenceEvent(BaseModel):
    """Event wrapper for asynchronous translation persistence."""
    event_id: str = Field(default_factory=generate_event_id)
    ticket_id: str
    customer_id: int
    translation_record: TranslationRecord
    created_at: datetime = Field(default_factory=generate_utc_now)
    source_system: str
    processing_status: str