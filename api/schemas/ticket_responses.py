from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
class TicketStatus:
    PROCESSING = "processing"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"

class TicketAcceptedResponse(BaseModel):
    status: str = Field(default="queued")
    detail: str = Field(..., description="Ticket accepted for processing")
    ticket_id: str = Field(..., description="The unified tracking identifier")

class TicketStatusResponse(BaseModel):
    ticket_id: str
    status: str
    agent_type: str | None = None
    workflow_status: str | None = None

class TicketResultResponse(BaseModel):
    ticket_id: str
    status: str
    specialist_result: dict | None = None
    customer_response: dict | None = None



class ContinueConversationResponse(BaseModel):
    ticket_id: str
    status: str
    detail: str

class TraceStepResponse(BaseModel):
    stage: str
    status: str
    details: Optional[str] = None
    created_at: datetime


class TicketTraceResponse(BaseModel):
    ticket_id: str
    total_steps: int
    steps: List[TraceStepResponse]