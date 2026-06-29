from pydantic import BaseModel


class TranslationRecord(BaseModel):
    ticket_id: str
    customer_id: int

    original_text: str
    original_language: str

    english_text: str

    response_english: str | None = None
    response_translated: str | None = None
    response_language: str | None = None

    translation_service: str

    translation_success: bool = True