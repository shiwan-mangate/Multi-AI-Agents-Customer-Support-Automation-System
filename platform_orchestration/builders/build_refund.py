# platform_orchestration/builders/build_refund.py

import logging

# Repositories
from layer_2_refund.repositories.customer_repository import CustomerRepository as RefundCustomerRepository
from layer_2_refund.repositories.order_repository import OrderRepository as RefundOrderRepository
from layer_2_refund.repositories.refund_repository import RefundRepository

# Services & Utilities
from layer_2_refund.services.mock_payment_service import MockPaymentService
from layer_2_refund.mappers.refund_output_mapper import build_refund_output
from platform_orchestration.adapters.refund_input_adapter import RefundInputAdapter
from layer_2_refund.graphs.state_factory import create_initial_refund_state

# GRAPH FACTORY
# ✅ FIX: Import the functional factory, NOT the static variable
from layer_2_refund.graphs.refund_graph import build_refund_graph

logger = logging.getLogger(__name__)

def build_refund(container):
    """Wires the Refund Agent dependencies and compiles its persistent graph."""
    logger.info("Building Layer 2: Refund Agent...")

    # 1. Repositories & Services
    container.refund_customer_repository = RefundCustomerRepository(container.db)
    container.refund_order_repository = RefundOrderRepository(container.db)
    container.refund_repository = RefundRepository(container.db)
    container.mock_payment_service = MockPaymentService()

    # 2. Graph Compilation
    # ✅ FIX: Dynamically compile the graph with the unified Postgres checkpointer
    container.refund_graph = build_refund_graph(checkpointer=container.checkpointer)

    # 3. Adapters & Factories
    container.refund_input_adapter = RefundInputAdapter()
    container.refund_state_factory = create_initial_refund_state
    container.build_refund_output = build_refund_output

    # 4. Orchestration Registry
    if not hasattr(container, "specialist_graphs"):
        container.specialist_graphs = {}
    if not hasattr(container, "output_mappers"):
        container.output_mappers = {}

    # Register for dynamic pipeline routing
    container.specialist_graphs["refund_agent"] = container.refund_graph
    container.output_mappers["refund_agent"] = build_refund_output
    
    logger.info("Refund Agent successfully wired into container.")