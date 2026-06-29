import logging

from langgraph.graph import StateGraph, START, END

# ❌ REMOVED: MemorySaver import

from ..schemas.faq_state import FAQState

from ..nodes.validate_contract_node import validate_contract_node
from ..nodes.query_understanding_node import query_understanding_node
from ..nodes.ambiguity_check_node import ambiguity_check_node
from ..nodes.clarification_node import clarification_node
from ..nodes.retrieval_strategy_node import retrieval_strategy_node

# 🟢 IMPORT THE NEW CLASS-BASED NODES
from ..nodes.retrieve_candidates_node import RetrieveCandidatesNode
from ..nodes.rerank_node import RerankNode

from ..nodes.parent_context_node import expand_parent_context_node
from ..nodes.generate_answer_node import generate_answer_node
from ..nodes.verify_answer_node import verify_answer_node
from ..nodes.confidence_gate_node import confidence_gate_node
from ..nodes.respond_node import respond_node

from ..routers.faq_routers import (
    route_after_validation,
    route_after_ambiguity,
    route_after_confidence
)

logger = logging.getLogger(__name__)


def escalation_handoff_node(state: FAQState):
    """
    Temporary terminal handoff until Escalation Agent exists.
    """
    return {
        "current_node": "escalation_handoff_node",
        "final_response": {
            "status": "handoff",
            "target": "escalation_agent",
            "reason": state.get(
                "escalation_reason",
                "FAQ agent unable to resolve."
            ),
            "knowledge_gap": state.get(
                "knowledge_gap_detected",
                False
            )
        }
    }


def route_after_retrieval(state: FAQState):
    """Stops pipeline if retrieval failed."""
    if state.get("knowledge_gap_detected") or state.get("escalation_required"):
        logger.warning("Routing to escalation after retrieval failure.")
        return "escalation_handoff_node"
    return "rerank_node"


def route_after_rerank(state: FAQState):
    """Stops pipeline if reranking failed."""
    if state.get("knowledge_gap_detected") or state.get("escalation_required"):
        logger.warning("Routing to escalation after rerank failure.")
        return "escalation_handoff_node"
    return "expand_parent_context_node"


def route_after_parent_expansion(state: FAQState):
    """Stops pipeline if parent expansion failed."""
    if state.get("knowledge_gap_detected") or state.get("escalation_required"):
        logger.warning("Routing to escalation after parent expansion failure.")
        return "escalation_handoff_node"
    return "generate_answer_node"


def route_after_generation(state: FAQState):
    """Stops pipeline if answer generation failed."""
    if state.get("escalation_required"):
        logger.warning("Routing to escalation after generation failure.")
        return "escalation_handoff_node"
    return "verify_answer_node"


# 🟢 ACCEPT THE CONTAINER AS AN ARGUMENT
def build_faq_graph(container):
    logger.info("Building FAQ graph with injected dependencies...")

    workflow = StateGraph(FAQState)

    # Standard Function Nodes
    workflow.add_node("validate_contract_node", validate_contract_node)
    workflow.add_node("query_understanding_node", query_understanding_node)
    workflow.add_node("ambiguity_check_node", ambiguity_check_node)
    workflow.add_node("clarification_node", clarification_node)
    workflow.add_node("retrieval_strategy_node", retrieval_strategy_node)
    
    # 🟢 INJECT HEAVY SERVICES INTO CLASS NODES
    # These use the FAQ DB (Port 5433) for knowledge!
    workflow.add_node(
        "retrieve_candidates_node", 
        RetrieveCandidatesNode(vector_store=container.vector_store)
    )
    workflow.add_node(
        "rerank_node", 
        RerankNode(reranker_service=container.reranker)
    )
    
    workflow.add_node("expand_parent_context_node", expand_parent_context_node)
    workflow.add_node("generate_answer_node", generate_answer_node)
    workflow.add_node("verify_answer_node", verify_answer_node)
    workflow.add_node("confidence_gate_node", confidence_gate_node)
    workflow.add_node("respond_node", respond_node)
    workflow.add_node("escalation_handoff_node", escalation_handoff_node)

    # Flow
    workflow.add_edge(START, "validate_contract_node")
    workflow.add_conditional_edges("validate_contract_node", route_after_validation)
    workflow.add_edge("query_understanding_node", "ambiguity_check_node")
    workflow.add_conditional_edges("ambiguity_check_node", route_after_ambiguity)
    workflow.add_edge("clarification_node", "query_understanding_node")
    workflow.add_edge("retrieval_strategy_node", "retrieve_candidates_node")
    workflow.add_conditional_edges("retrieve_candidates_node", route_after_retrieval)
    workflow.add_conditional_edges("rerank_node", route_after_rerank)
    workflow.add_conditional_edges("expand_parent_context_node", route_after_parent_expansion)
    workflow.add_conditional_edges("generate_answer_node", route_after_generation)
    workflow.add_edge("verify_answer_node", "confidence_gate_node")
    workflow.add_conditional_edges("confidence_gate_node", route_after_confidence)
    workflow.add_edge("respond_node", END)
    workflow.add_edge("escalation_handoff_node", END)

    # ✅ INJECTED: Uses the shared checkpointer (Main DB - Port 5432) for state memory
    app = workflow.compile(checkpointer=container.checkpointer)

    logger.info("FAQ graph compiled.")
    return app