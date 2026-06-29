from pydantic import BaseModel, Field
from typing import List, Dict, Any
from datetime import datetime

class ProactiveEventItem(BaseModel):
    workflow_id: str
    customer_id: int
    signal_type: str
    outreach_status: str
    created_at: datetime
    metadata: Dict[str, Any] = Field(default_factory=dict)

class ProactiveHistoryResponse(BaseModel):
    customer_id: int
    total_events: int
    events: List[ProactiveEventItem]

class SuppressionItem(BaseModel):
    customer_id: int
    signal_type: str
    reason: str | None = None
    expires_at: datetime

class ActiveSuppressionsResponse(BaseModel):
    customer_id: int
    active_cooldowns: int
    suppressions: List[SuppressionItem]

class DetectedSignalItem(BaseModel):
    signal_id: str
    customer_id: int
    signal_type: str
    signal_source: str
    signal_context: Dict[str, Any]

class ActiveSignalsResponse(BaseModel):
    total_detected: int
    signals: List[DetectedSignalItem]

class RunScanResponse(BaseModel):
    status: str
    detail: str
    signals_detected: int
    signals_dispatched: int

class RecentEventsResponse(BaseModel):
    total_events: int
    events: List[ProactiveEventItem]