# platform_orchestration/builders/build_triage.py

import logging
from layer_2_triage.repositories.customer_repository import CustomerRepository as TriageCustomerRepository
from layer_2_triage.repositories.ticket_repository import TicketRepository as TriageTicketRepository
from layer_2_triage.repositories.order_repository import OrderRepository as TriageOrderRepository
from platform_orchestration.specialist_router import SpecialistRouter

# GRAPH FACTORIES
from layer_2_triage.graphs.triage_graph import build_triage_graph  
from layer_2_triage.graphs.state_factory import TriageStateFactory

logger = logging.getLogger(__name__)

def build_triage(container):
    """Wires the Layer 2 Triage dependencies and compiles its persistent graph."""
    logger.info("Building Layer 2: Triage Agent...")
    
    # 1. Initialize Repositories (Sharing master DB session)
    container.triage_customer_repository = TriageCustomerRepository(container.db)
    container.triage_ticket_repository = TriageTicketRepository(container.db)
    container.triage_order_repository = TriageOrderRepository(container.db)
    container.triage_state_factory = TriageStateFactory()
    
    # 2. Graph Compilation
    # ✅ FIX: Pass the shared platform checkpointer straight into the Triage graph compiler
    container.triage_graph = build_triage_graph(
    checkpointer=None
)
    
    # 3. Router Orchestration
    container.specialist_router = SpecialistRouter(container)

    logger.info("Triage Agent successfully wired into container.")