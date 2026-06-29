from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime

class TranslationRecordItem(BaseModel):
    """Represents a single bidirectional translation audit log."""
    ticket_id: str
    customer_id: int
    original_language: str
    translation_success: bool
    
    original_text: Optional[str] = None
    english_text: Optional[str] = None
    
    response_english: Optional[str] = None
    response_translated: Optional[str] = None
    response_language: Optional[str] = None
    
    created_at: Optional[datetime] = None

class CustomerTranslationHistoryResponse(BaseModel):
    customer_id: int
    total_records: int
    history: List[TranslationRecordItem]

class LiveTranslationResponse(BaseModel):
    ticket_id: str
    target_language: str
    translation_success: bool
    translated_text: str
    provider_used: str

class OperationsDashboardResponse(BaseModel):
    """Wraps the LanguageDashboardService operations payload."""
    generated_at: str
    dashboard_type: str
    status: str
    is_alerting: bool = False
    system_health: Dict[str, Any]
    failure_metrics: Dict[str, Any]
    error: Optional[str] = None