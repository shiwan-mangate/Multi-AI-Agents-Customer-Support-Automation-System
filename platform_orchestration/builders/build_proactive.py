# platform_orchestration/builders/build_proactive.py

import os
import logging
from langchain_groq import ChatGroq

# REPOSITORIES
from layer_2_proactive_agent.repositories.proactive_event_repository import ProactiveEventRepository
from layer_2_proactive_agent.repositories.proactive_outreach_repository import ProactiveOutreachRepository

# SERVICES
from layer_2_proactive_agent.services.signal_detection_service import SignalDetectionService
from layer_2_proactive_agent.services.risk_engine import RiskEngine
from layer_2_proactive_agent.services.outreach_decision_service import OutreachDecisionService
from layer_2_proactive_agent.services.message_generation_service import MessageGenerationService
from layer_2_proactive_agent.services.escalation_service import EscalationService
from layer_2_proactive_agent.services.suppression_service import SuppressionService

# GRAPH & STATE
# ✅ FIX: Import the build function factory, NOT the variable
from layer_2_proactive_agent.graph.proactive_graph import build_proactive_graph
from layer_2_proactive_agent.graph.state_factory import ProactiveStateFactory

# ADAPTERS
from layer_2_proactive_agent.adapters.proactive_adapter import ProactiveAdapter

logger = logging.getLogger(__name__)

def build_proactive(container):
    """
    Wires the Layer 2 Proactive Agent dependencies into the global container.
    """
    logger.info("Building Layer 2: Proactive Agent...")

    # 1. REPOSITORIES
    container.proactive_event_repository = ProactiveEventRepository(container.db)
    container.proactive_outreach_repository = ProactiveOutreachRepository(container.db)

    # 2. CORE INTELLIGENCE SERVICES
    container.proactive_signal_service = SignalDetectionService()
    container.proactive_risk_engine = RiskEngine()
    container.proactive_decision_service = OutreachDecisionService()

    # 3. LLM MESSAGE GENERATION SERVICE
    proactive_llm = ChatGroq(
        model_name="openai/gpt-oss-120b",
        temperature=0.3,
        api_key=os.getenv("GROQ_API_KEY"),
        max_retries=2
    )
    container.proactive_message_service = MessageGenerationService(llm=proactive_llm)

    # 4. ORCHESTRATION & HANDOFF SERVICES
    container.proactive_escalation_service = EscalationService()
    container.proactive_suppression_service = SuppressionService(
        repo=container.proactive_outreach_repository
    )

    # 5. ADAPTER & UTILITIES
    container.proactive_adapter = ProactiveAdapter()
    container.proactive_state_factory = ProactiveStateFactory()

    # 6. GRAPH COMPILATION
    # ✅ FIX: Compile the graph dynamically using the shared Postgres checkpointer
    container.proactive_graph = build_proactive_graph(checkpointer=container.checkpointer)

    # 7. REGISTRY
    if not hasattr(container, "specialist_graphs"):
        container.specialist_graphs = {}
        
    container.specialist_graphs["proactive_agent"] = container.proactive_graph

    logger.info("Proactive Agent successfully wired into container.")