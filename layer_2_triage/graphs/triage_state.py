from typing import TypedDict, List, Optional, Dict, Any, Union
from datetime import datetime

class TicketPayload(TypedDict):
    """Schema for the original incoming ticket data."""
    ticket_id: str
    channel: str
    customer_id: str
    message_raw: str
    message_english: str
    timestamp: datetime

class ExtractedEntities(TypedDict):
    """Schema for entities extracted by the Layer 1 Supervisor."""
    # Note: order_id is integer in DB (orders table), kept as str/int for compatibility
    order_id: Optional[Union[str, int]]
    product_name: Optional[str]
    amount: Optional[float]
    purchase_date: Optional[str]
    shipping_address: Optional[str]

class WorkflowLog(TypedDict):
    """Schema for structured observability logs."""
    timestamp: str  # Changed to str to match isoformat() usage in nodes
    node: str
    message: str
    data: Optional[Dict[str, Any]]

class OrderContext(TypedDict):
    """
    Refined Transactional Context.
    Created_at is now a native datetime object for easier date math.
    """
    order_id: int
    amount: float
    status: str
    created_at: datetime




# --- 2. MAIN TRIAGE STATE ---

class TriageState(TypedDict):
    ticket: TicketPayload 
    entities: ExtractedEntities
    ticket_id: str
    initial_intent: str
    customer_email: str
    customer_id: Optional[int] # Aligns with bigint in DB
    
    initial_urgency: str
    initial_sentiment: str
    supervisor_confidence: float 

    # --- POSTGRESQL CRM CONTEXT ---
    # Aligns with 'customers' table (account_tier: varchar, total_spent: numeric)
    customer_tier: Optional[str] 
    ltv: Optional[float]
    unresolved_repeat_count: int
    total_tickets: int
    total_escalations: int
    last_sentiment: Optional[str]
    order_context: Optional[OrderContext]

    # --- DETERMINISTIC SCORING ---
    urgency_score: Optional[float]
    ltv_score: Optional[float]
    sentiment_score: Optional[float]
    history_score: Optional[float]
    final_score: Optional[float]

    # --- FINAL TRIAGE DECISIONS ---
    final_priority: Optional[str] 
    sla_duration_hours: Optional[int]
    sla_deadline: Optional[datetime] 

    # --- AGENTIC INTELLIGENCE ---
    insight_tags: List[str] 
    escalation_required: bool
    escalation_reason: Optional[str]

    # --- ROUTING & METADATA ---
    created_at: datetime 
    next_agent: Optional[str] 
    current_node: str 
    workflow_logs: List[WorkflowLog]