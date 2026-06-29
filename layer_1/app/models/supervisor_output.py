## layer_1/app/models/supervisor_output.py
from pydantic import BaseModel, Field
from typing import  Dict, Literal, Optional, Union

class SupervisorOutput(BaseModel):
    ticket_id: str
    intent: Literal["faq", "refund_request", "account_issue", "technical_bug", "angry_complex"]
    confidence: int = Field(..., ge=0, le=100, description="Certainty score for the chosen intent")
    sentiment: Literal["positive", "neutral", "frustrated", "angry"]
    urgency: Literal["low", "medium", "high", "urgent"]

    decision_summary: str = Field(...,description="Short operational explanation for routing decision")

    route_to: Literal[
        "faq_agent", 
        "refund_agent", 
        "account_agent", 
        "technical_agent", 
        "escalation_agent", 
        "clarification_flow"
    ]
    review_required: bool = Field(default=False, description="Flag for human-in-the-loop if confidence is borderline")

    clarifying_question: Optional[str] = Field(
        None, description="Question to be sent to user if route_to is 'clarification_flow'"
    )
    
    entities: Dict[str, Optional[Union[str, int, float]]]= Field(
        default_factory=dict, 
        description="Extracted facts like order_id, product_name, email, etc."
    )

    supervisor_notes: str = Field(..., description="Technical summary handed to the specialist agent")