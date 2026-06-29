from typing import Optional
from pydantic import BaseModel, Field


class LanguageContext(BaseModel):
    detected_language: str
    detection_confidence: float

    detection_method: str

    translation_used: bool

    translation_failed: bool = False
    fallback_triggered: bool = False

    mixed_language_detected: bool = False

    script_detected: Optional[str] = None

    original_message_stored: bool = True