# platform_orchestration/specialist_router.py
import logging
logger = logging.getLogger("specialist_router")

class SpecialistRouter:
    """
    The Dynamic Dispatcher.
    Reads the Layer 2 Triage routing decision and returns the correct
    compiled LangGraph object for the specialized domain agent.
    """
    def __init__(self, container):
        self.container = container

    def route(self, triage_result):

        if isinstance(triage_result, dict):
            agent = triage_result.get("next_agent", "escalation_agent")
        else:
            agent = getattr(triage_result, "next_agent", "escalation_agent")
            
        logger.info(f"SpecialistRouter | Target Identified: {agent}")


        if agent == "refund_agent":
            return getattr(self.container, "refund_graph", "REFUND_GRAPH_NOT_INITIALIZED")
            
        if agent == "account_agent":
            return getattr(self.container, "account_graph", "ACCOUNT_GRAPH_NOT_INITIALIZED")
            
        if agent == "faq_agent":
            return getattr(self.container, "faq_graph", "FAQ_GRAPH_NOT_INITIALIZED")
            
        return getattr(self.container, "escalation_graph", "ESCALATION_GRAPH_NOT_INITIALIZED")
    