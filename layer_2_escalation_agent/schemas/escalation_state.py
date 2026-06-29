from typing import TypedDict, Dict, Any, List, Optional

from .trigger_assessment import TriggerAssessment
from .customer_context import CustomerContext
from .conversation_context import ConversationContext
from .risk_assessment import RiskAssessment
from .human_brief import HumanBrief
from .routing_decision import RoutingDecision
from .notification_job import NotificationJob
from .escalation_response import EscalationResponse
from .human_decision import HumanDecision


class EscalationState(TypedDict):
    ticket: Dict[str, Any]
    ticket_id: str                      
    customer_id: int                   
    customer_email: str
    source_agent: str
    initial_intent: str
    initial_sentiment: str
    initial_urgency: str
    supervisor_confidence: float
    entities: List[Dict[str, Any]]      
    workflow_logs: List[Dict[str, Any]]

    trigger_assessment: Optional[TriggerAssessment]
    customer_context: Optional[CustomerContext]
    conversation_context: Optional[ConversationContext]
    risk_assessment: Optional[RiskAssessment]

    holding_message: Optional[str]
    holding_sent: bool

    human_brief: Optional[HumanBrief]
    routing_decision: Optional[RoutingDecision]

    review_required: bool              
    review_completed: bool          
    human_decision: Optional[HumanDecision]

    case_id: Optional[str]
    notification_jobs: List[NotificationJob]

    response: Optional[EscalationResponse]

    current_node: str
    errors: List[str]
    metrics: Dict[str, Any]

    audit_status: Optional[str]