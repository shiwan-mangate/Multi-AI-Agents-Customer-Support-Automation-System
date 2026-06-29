import logging
from langgraph.graph import StateGraph, START, END

from layer_2_proactive_agent.schemas.proactive_state import ProactiveState

# Nodes
from layer_2_proactive_agent.nodes.validate_signal_node import validate_signal_node
from layer_2_proactive_agent.nodes.customer_context_node import customer_context_node
from layer_2_proactive_agent.nodes.suppression_gate_node import suppression_gate_node
from layer_2_proactive_agent.nodes.signal_analysis_node import signal_analysis_node
from layer_2_proactive_agent.nodes.risk_scoring_node import risk_scoring_node
from layer_2_proactive_agent.nodes.outreach_decision_node import outreach_decision_node
from layer_2_proactive_agent.nodes.message_generation_node import message_generation_node
from layer_2_proactive_agent.nodes.escalation_handoff_node import escalation_handoff_node
from layer_2_proactive_agent.nodes.response_node import response_node

# Routers
from layer_2_proactive_agent.graph.routers import (
    suppression_router,
    decision_router,
)

logger = logging.getLogger(__name__)
GRAPH_NAME = "proactive_agent"


def build_proactive_graph(checkpointer):
    """
    Assembles the decoupled Proactive Agent State Machine.
    Outputs a clean ProactiveOutput contract.
    """
    
    graph = StateGraph(ProactiveState)

    # 1. Add Nodes
    graph.add_node("validate_signal_node", validate_signal_node)
    graph.add_node("customer_context_node", customer_context_node)
    graph.add_node("suppression_gate_node", suppression_gate_node)
    
    graph.add_node("signal_analysis_node", signal_analysis_node)
    graph.add_node("risk_scoring_node", risk_scoring_node)
    graph.add_node("outreach_decision_node", outreach_decision_node)
    
    graph.add_node("message_generation_node", message_generation_node)
    graph.add_node("escalation_handoff_node", escalation_handoff_node)
    
    graph.add_node("response_node", response_node)

    # 2. Define Flow
    graph.add_edge(START, "validate_signal_node")
    graph.add_edge("validate_signal_node", "customer_context_node")
    graph.add_edge("customer_context_node", "suppression_gate_node")

    # Suppression Conditional Routing
    graph.add_conditional_edges(
        "suppression_gate_node",
        suppression_router,
        {
            "signal_analysis_node": "signal_analysis_node",
            "response_node": "response_node",  
        },
    )

    graph.add_edge("signal_analysis_node", "risk_scoring_node")
    graph.add_edge("risk_scoring_node", "outreach_decision_node")

    # Outreach Strategy Conditional Routing
    graph.add_conditional_edges(
        "outreach_decision_node",
        decision_router,
        {
            "message_generation_node": "message_generation_node",
            "escalation_handoff_node": "escalation_handoff_node",
            "response_node": "response_node",  
        },
    )

    graph.add_edge("message_generation_node", "response_node") 
    graph.add_edge("escalation_handoff_node", "response_node")
    
    graph.add_edge("response_node", END)


    logger.info(f"Compiling {GRAPH_NAME} with persistent checkpointer...")
    return graph.compile(
        checkpointer=checkpointer,
        name=GRAPH_NAME,
    )

