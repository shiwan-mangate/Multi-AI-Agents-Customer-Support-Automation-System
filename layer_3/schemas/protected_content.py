from pydantic import BaseModel, Field
from typing import Dict

class ProtectedContent(BaseModel):
    original_text: str
    protected_text: str
    entity_placeholders: Dict[str, str] = Field(default_factory=dict)
    format_placeholders: Dict[str, str] = Field(default_factory=dict)
    entity_count: int = 0
    format_count: int = 0