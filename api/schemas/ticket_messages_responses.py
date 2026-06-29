from pydantic import BaseModel, Field
from typing import Any, Dict, List
from datetime import datetime


class ConversationMessage(BaseModel):
    """
    Generic message object stored inside transcript.messages.
    We intentionally keep it flexible because different agents
    may store slightly different structures.
    """
    data: Dict[str, Any]


class TicketMessagesResponse(BaseModel):
    ticket_id: str
    customer_id: int
    source_agent: str
    status: str
    created_at: datetime

    total_messages: int

    messages: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Raw conversation history stored in CRM transcript ledger."
    )