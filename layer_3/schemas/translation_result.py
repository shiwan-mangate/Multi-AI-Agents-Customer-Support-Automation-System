from pydantic import BaseModel


class TranslationResult(BaseModel):
    translated_text: str

    source_language: str
    target_language: str

    translation_service: str

    translation_success: bool = True

    translation_confidence: float | None = None