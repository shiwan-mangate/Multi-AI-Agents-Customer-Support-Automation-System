from langgraph.graph import StateGraph, START, END

# ❌ REMOVED: MemorySaver import
# ❌ REMOVED: DependencyContainer import (we will inject it instead)

from layer_2_triage.graphs.triage_state import TriageState
from layer_2_triage.graphs.nodes.fetch_customer_node import fetch_customer_node
from layer_2_triage.graphs.nodes.fetch_order_node import fetch_order_node
from layer_2_triage.graphs.nodes.history_node import history_node
from layer_2_triage.graphs.nodes.scoring_node import scoring_node
from layer_2_triage.graphs.nodes.priority_node import priority_node
from layer_2_triage.graphs.nodes.sla_node import sla_node
from layer_2_triage.graphs.nodes.escalation_check_node import escalation_check_node
from layer_2_triage.graphs.nodes.dispatch_node import dispatch_node

# ✅ ADDED: checkpointer as a required parameter
def build_triage_graph(checkpointer):
    """
    Assembles the Layer 2 Triage state machine.
    
    Flow: 
    Enrichment (Identity/Transaction) -> History Analysis -> Scoring -> 
    Priority Mapping -> SLA Commitment -> Escalation Policy -> Dispatch.
    """
    
    builder = StateGraph(TriageState)

    # 1. Add Nodes
    builder.add_node("fetch_customer", fetch_customer_node)
    builder.add_node("fetch_order", fetch_order_node)
    builder.add_node("history", history_node)
    builder.add_node("scoring", scoring_node)
    builder.add_node("priority", priority_node)
    builder.add_node("sla", sla_node)
    builder.add_node("escalation_check", escalation_check_node)
    builder.add_node("dispatch", dispatch_node)

    # 2. Define Sequential Flow
    builder.add_edge(START, "fetch_customer")
    builder.add_edge("fetch_customer", "fetch_order")
    builder.add_edge("fetch_order", "history")
    builder.add_edge("history", "scoring")
    builder.add_edge("scoring", "priority")
    builder.add_edge("priority", "sla")
    builder.add_edge("sla", "escalation_check")
    builder.add_edge("escalation_check", "dispatch")
    builder.add_edge("dispatch", END)

    # 3. Compilation with Persistent Postgres Checkpointer
    # ✅ INJECTED: Uses the shared checkpointer passed from the container
    triage_app = builder.compile(checkpointer=checkpointer)
    
    return triage_app