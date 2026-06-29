from typing import Optional, Any
from pydantic import BaseModel

from .escalation_response import EscalationResponse


class EscalationAgentResponse(BaseModel):
    ticket_id: str
    source_agent: str

    status: str

    thread_id: Optional[str] = None

    response: Optional[EscalationResponse] = None

    review_payload: Optional[dict[str, Any]] = None
    duration_ms: Optional[int] = None
    error: Optional[str] = None
    
    customer_facing_response: Optional[str] = None