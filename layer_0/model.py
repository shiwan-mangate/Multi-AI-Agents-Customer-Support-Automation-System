from typing import Optional, Literal
from pydantic import BaseModel
from pydantic import Field
from typing import List, Dict, Any
class CustomerInfo(BaseModel):
    lifetime_value: float
    previous_tickets: int
    tier: Literal["standard", "premium", "enterprise"] # FIX: Enforced

class RequestModel(BaseModel):
    message: str
    customer_id: int
    name: str

class UnifiedTicket(BaseModel):
    ticket_id: str                 
    channel: str
    customer_id: int               
    customer_name: str
    timestamp: str
    issue_description: str
    message_text: str
    conversation_history: List[Dict[str, Any]] = Field(
    default_factory=list
)
    language: Literal["en", "hi", "es", "fr", "de", "ar"] # FIX: Enforced
    intent: Optional[Literal["faq", "refund_request", "account_issue", "technical_bug", "angry_complex"]] = None # FIX: Enforced
    order_id: Optional[int] = None  
    issue_type: Optional[str] = None
    customer_info: Optional[CustomerInfo] = None
    priority: Optional[Literal["low", "medium", "high", "urgent"]] = None # FIX: Enforced