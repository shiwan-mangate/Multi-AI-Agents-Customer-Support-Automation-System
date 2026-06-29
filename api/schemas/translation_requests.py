from pydantic import BaseModel, Field
from typing import Optional

class LiveTranslationRequest(BaseModel):
    """Payload for manually triggering an outbound translation."""
    english_text: str = Field(..., description="The English text the manager wants to send.")
    target_language: str = Field(..., description="ISO language code (e.g., 'es', 'fr', 'hi').")
    source_agent: Optional[str] = Field(
        "human_manager", 
        description="Used by the ToneAdjustmentService to format the prefix."
    )