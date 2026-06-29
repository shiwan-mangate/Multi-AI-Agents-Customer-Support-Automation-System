from pydantic import BaseModel
from .language_context import LanguageContext

class BilingualMessage(BaseModel):
    original_text: str
    english_text: str
    language_context: LanguageContext