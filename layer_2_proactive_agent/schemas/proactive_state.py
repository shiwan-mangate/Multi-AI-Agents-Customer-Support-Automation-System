from typing import TypedDict, Optional, List

from crm_agent.schemas.customer_profile import CustomerProfile

from layer_2_proactive_agent.schemas.signal import Signal
from layer_2_proactive_agent.schemas.signal_assessment import SignalAssessment
from layer_2_proactive_agent.schemas.risk_assessment import RiskAssessment
from layer_2_proactive_agent.schemas.outreach_decision import OutreachDecision
from layer_2_proactive_agent.schemas.outreach_message import OutreachMessage
from layer_2_proactive_agent.schemas.escalation_handoff import EscalationHandoff
from layer_2_proactive_agent.schemas.proactive_output import ProactiveOutput
from typing import TypedDict, Optional, List, Dict, Any

class ProactiveState(TypedDict):
    """
    LangGraph workflow state.

    Mutable orchestration memory shared
    across all graph nodes.
    """

    workflow_id: str
    signal_id: str
    status: str
    signal: Signal
    customer_profile: Optional[CustomerProfile]
    signal_assessment: Optional[SignalAssessment]
    risk_assessment: Optional[RiskAssessment]
    decision: Optional[OutreachDecision]
    outreach_message: Optional[OutreachMessage]
    escalation_handoff: Optional[EscalationHandoff]
    output: Optional[ProactiveOutput]
    suppressed: bool
    suppression_reason: Optional[str]
    current_node: Optional[str]
    workflow_logs: List[Dict[str, Any]]  
    errors: List[str]