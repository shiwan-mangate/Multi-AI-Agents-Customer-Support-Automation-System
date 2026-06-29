from typing import TypedDict, Optional, List
from datetime import datetime

class TriageOutput(TypedDict):
    ticket_id: str

    customer_id: Optional[int]
    customer_email: str
    customer_tier: Optional[str]
    ltv: Optional[float]

    initial_intent: str
    initial_urgency: str
    initial_sentiment: str
    supervisor_confidence: float

    entities: dict

    order_context: Optional[dict]

    final_score: Optional[float]
    final_priority: Optional[str]

    sla_duration_hours: Optional[int]
    sla_deadline: Optional[datetime]

    escalation_required: bool
    escalation_reason: Optional[str]

    insight_tags: List[str]

    next_agent: Optional[str]

    triage_completed_at: datetime