from pydantic import BaseModel
from typing import Optional

class TranslationRequest(BaseModel):
    """
    Canonical representation of a translation request.
    Produced by SpecialistResponseAdapter, consumed by TranslationService.
    """
    ticket_id: str
    source_agent: str
    english_response: str
    target_language: str
    customer_id: int | None = None