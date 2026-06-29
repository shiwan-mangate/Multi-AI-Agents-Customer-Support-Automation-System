from typing import Literal
from ..schemas.faq_state import FAQState

def route_after_ambiguity(state: FAQState) -> Literal["clarification_node", "retrieval_strategy_node", "escalation_agent"]:
    """
    Determines if the agent understands the customer's intent well enough 
    to proceed or if it needs to pause for clarification.
    
    Strictly handles None values to prevent undefined behavior.
    """
    ambiguity = state.get("ambiguity_detected")

    if ambiguity is True:
        return "clarification_node"
    
    if ambiguity is False:
        return "retrieval_strategy_node"
    

    return "escalation_agent"


def route_after_confidence(state: FAQState) -> Literal["respond_node", "query_understanding_node", "escalation_agent"]:
    """
    The final decision gate. Implements threshold-based routing, 
    hallucination hard-stops, and bounded retry logic.
    """
    score = state.get("confidence_score")
    verifier_score = state.get("verifier_score")
    retries = state.get("retry_count") or 0
    

    if score is None or verifier_score is None or verifier_score == 0.0:
        return "escalation_agent"
    
  
    if score >= 0.80:
        return "respond_node"

    if 0.55 <= score < 0.80 and retries < 1:
        return "query_understanding_node"

    return "escalation_agent"