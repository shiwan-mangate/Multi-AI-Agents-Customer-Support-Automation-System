# layer_2_faq/schemas/faq_output.py

from typing import Optional, List, Literal
from datetime import datetime, UTC
from .faq_models import FAQBaseModel, Citation

class FAQAgentOutput(FAQBaseModel):
    """
    Final business output emitted by the FAQ Agent.
    """
    ticket_id: str
    customer_id: int
    assigned_agent: Literal["faq_agent"] = "faq_agent"
    status: Literal[
        "resolved",
        "clarification_required",
        "escalated",
        "failed"
    ]
    decision_target: Literal[
        "customer",
        "escalation_agent"
    ]
    answer: Optional[str] = None
    citations: List[Citation] = []
    
    # Strict Types (Cannot be None)
    confidence_score: float = 0.0
    verifier_score: Optional[float] = None
    knowledge_gap_detected: bool = False
    knowledge_gap_reason: Optional[str] = None
    clarification_question: Optional[str] = None
    escalation_required: bool = False
    escalation_reason: Optional[str] = None
    query_intent: Optional[str] = None
    retrieval_strategy: Optional[str] = None
    retry_count: int = 0
    completed_at: datetime
    duration_ms: Optional[int] = None