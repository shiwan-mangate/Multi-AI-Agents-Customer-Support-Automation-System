# platform_orchestration/builders/build_escalation.py

import logging
import os

# Repositories
from layer_2_escalation_agent.repositories.audit_repository import AuditRepository
from layer_2_escalation_agent.repositories.conversation_repository import ConversationRepository
from layer_2_escalation_agent.repositories.customer_repository import CustomerRepository as EscalationCustomerRepository
from layer_2_escalation_agent.repositories.escalation_repository import EscalationRepository
from layer_2_escalation_agent.repositories.notification_outbox_repository import NotificationOutboxRepository
from layer_2_escalation_agent.repositories.ticket_repository import TicketRepository as EscalationTicketRepository

# Services
from layer_2_escalation_agent.services.brief_generation_service import HumanBriefService
from layer_2_escalation_agent.services.holding_response_service import HoldingResponseService
from layer_2_escalation_agent.services.notification_service import NotificationService
from layer_2_escalation_agent.services.risk_engine import RiskEngine as EscalationRiskEngine
from layer_2_escalation_agent.services.routing_service import RoutingService
from layer_2_escalation_agent.services.trigger_engine import TriggerEngine

# Orchestration Components
from layer_2_escalation_agent.graph.escalation_graph import build_escalation_graph
from layer_2_escalation_agent.factories.state_factory import EscalationStateFactory
from platform_orchestration.adapters.escalation_input_adapter import EscalationInputAdapter
from layer_2_escalation_agent.mapper.escalation_final_responce import build_escalation_output

logger = logging.getLogger(__name__)

def build_escalation(container):
    """Wires the Escalation Agent and its dependencies into the global container."""
    logger.info("Building Layer 2: Escalation Agent...")

    # ==========================================
    # 1. REPOSITORIES (Sharing the master DB session)
    # ==========================================
    container.escalation_repository = EscalationRepository(container.db)
    container.notification_outbox_repository = NotificationOutboxRepository(container.db)
    container.escalation_ticket_repository = EscalationTicketRepository(container.db)
    container.escalation_customer_repository = EscalationCustomerRepository(container.db)
    container.conversation_repository = ConversationRepository(container.db)
    container.audit_repository = AuditRepository(container.db)

    # ==========================================
    # 2. SERVICES
    # ==========================================
    container.human_brief_service = HumanBriefService(llm_client=container.llm)
    container.holding_response_service = HoldingResponseService()
    container.notification_service = NotificationService()
    container.escalation_risk_engine = EscalationRiskEngine()
    container.routing_service = RoutingService()
    container.trigger_engine = TriggerEngine()

    # ==========================================
    # 3. UTILITIES & ADAPTERS
    # ==========================================
    container.escalation_input_adapter = EscalationInputAdapter()
    container.escalation_state_factory = EscalationStateFactory()
    container.build_escalation_output = build_escalation_output

    # ==========================================
    # 4. GRAPH COMPILATION
    # ==========================================
    # Read HITL configuration from environment variables if present, default to True
    enable_hitl = os.getenv("ENABLE_HITL", "True").lower() in ("true", "1", "yes")
    
    # ✅ FIX: Explicitly pass configuration parameters into the graph factory
    container.escalation_graph = build_escalation_graph(container, enable_hitl=enable_hitl)

    # ==========================================
    # 5. ORCHESTRATION REGISTRY
    # ==========================================
    if not hasattr(container, "specialist_graphs"):
        container.specialist_graphs = {}
    if not hasattr(container, "output_mappers"):
        container.output_mappers = {}

    # Register for dynamic routing
    container.specialist_graphs["escalation_agent"] = container.escalation_graph
    container.output_mappers["escalation_agent"] = build_escalation_output

    logger.info("Escalation Agent successfully wired into container.")