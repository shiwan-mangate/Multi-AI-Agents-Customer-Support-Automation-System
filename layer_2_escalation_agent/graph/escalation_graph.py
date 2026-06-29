import logging
from datetime import datetime, UTC
from langgraph.graph import StateGraph, END
from layer_2_escalation_agent.schemas.escalation_state import EscalationState
from layer_2_escalation_agent.schemas.human_decision import HumanDecision, HumanDecisionType
from layer_2_escalation_agent.graph.routers import route_validation, route_duplicate_case
from layer_2_escalation_agent.nodes.validate_contract_node import validate_contract_node
from layer_2_escalation_agent.nodes.trigger_assessment_node import trigger_assessment_node
from layer_2_escalation_agent.nodes.customer_context_node import customer_context_node
from layer_2_escalation_agent.nodes.conversation_context_node import conversation_context_node
from layer_2_escalation_agent.nodes.risk_scoring_node import risk_scoring_node
from layer_2_escalation_agent.nodes.routing_decision_node import routing_decision_node
from layer_2_escalation_agent.nodes.holding_response_node import holding_response_node
from layer_2_escalation_agent.nodes.brief_generation_node import brief_generation_node
from layer_2_escalation_agent.nodes.human_review_node import human_review_node
from layer_2_escalation_agent.nodes.notification_dispatch_node import notification_dispatch_node
from layer_2_escalation_agent.nodes.case_persistence_node import case_persistence_node
from layer_2_escalation_agent.nodes.response_node import response_node

logger = logging.getLogger(__name__)


def dev_auto_approve_node(state: EscalationState) -> EscalationState:
    """
    Mock node for local development. 
    Fulfills the strict governance data contract so downstream nodes don't crash.
    """
    logger.info("Executing dev_auto_approve (HITL Bypass)")
    
    state["current_node"] = "dev_auto_approve"
    
    decision_val = HumanDecisionType.APPROVE.value if hasattr(HumanDecisionType.APPROVE, "value") else "APPROVE"

    state["human_decision"] = HumanDecision(
        decision=decision_val,
        reviewer_id="dev_bypass_system",
        notes="Auto-approved via local enable_hitl=False flag."
    )
    state["review_completed"] = True
    state["review_required"] = False
    
    state["workflow_logs"].append({
        "node": "dev_auto_approve",
        "timestamp": datetime.now(UTC).isoformat(),
        "message": "Dev auto-approval bypass applied.",
        "data": {
            "review_required": False,
            "decision": "approve",
        },
    })
    
    return state


def build_escalation_graph(container, enable_hitl: bool = True):
    """
    Build escalation workflow using Dependency Injection.

    enable_hitl=True:
        Production mode with human approval state suspension.
    enable_hitl=False:
        Dev/local mode with automatic workflow continuation.
    """
    builder = StateGraph(EscalationState)

    # ==========================================
    # 1. CORE NODES (Using container injections)
    # ==========================================
  
    # Pure state nodes (no external dependencies)
    builder.add_node("validate_contract", validate_contract_node)
    builder.add_node("human_review", human_review_node)
    builder.add_node("response", response_node)

    # Injected nodes
    builder.add_node(
        "trigger_assessment", 
        lambda state: trigger_assessment_node(
            state, 
            container.trigger_engine, 
            container.escalation_repository
        )
    )
    
    builder.add_node(
        "customer_context", 
        lambda state: customer_context_node(
            state, 
            container.escalation_customer_repository, 
            container.escalation_ticket_repository
        )
    )
    
    builder.add_node(
        "conversation_context", 
        lambda state: conversation_context_node(
            state, 
            container.conversation_repository
        )
    )
    
    builder.add_node(
        "risk_scoring", 
        lambda state: risk_scoring_node(
            state, 
            container.escalation_risk_engine
        )
    )
    
    builder.add_node(
        "routing_decision", 
        lambda state: routing_decision_node(
            state, 
            container.routing_service
        )
    )
    
    builder.add_node(
        "holding_response", 
        lambda state: holding_response_node(
            state, 
            container.holding_response_service
        )
    )
    
    builder.add_node(
        "brief_generation", 
        lambda state: brief_generation_node(
            state, 
            container.human_brief_service
        )
    )
    
    builder.add_node(
        "notification_dispatch", 
        lambda state: notification_dispatch_node(
            state, 
            container.notification_service
        )
    )
    
    builder.add_node(
        "case_persistence", 
        lambda state: case_persistence_node(
            state, 
            container.escalation_repository,
            container.audit_repository,
            container.notification_outbox_repository
        )
    )

    # ==========================================
    # 2. EDGES & ROUTING
    # ==========================================
  
    builder.set_entry_point("validate_contract")

    builder.add_conditional_edges(
        "validate_contract",
        route_validation,
        {
            "valid": "trigger_assessment",
            "invalid": "response",
        },
    )

    builder.add_conditional_edges(
        "trigger_assessment",
        route_duplicate_case,
        {
            "duplicate": "response",
            "continue": "customer_context",
        },
    )

    builder.add_edge("customer_context", "conversation_context")
    builder.add_edge("conversation_context", "risk_scoring")
    builder.add_edge("risk_scoring", "routing_decision")
    builder.add_edge("routing_decision", "holding_response")
    builder.add_edge("holding_response", "brief_generation")

    # Dynamic HITL / Local Dev Branching Switch
    if enable_hitl:
        builder.add_edge("brief_generation", "human_review")
        builder.add_edge("human_review", "notification_dispatch")
    else:
        builder.add_node("dev_auto_approve", dev_auto_approve_node)
        builder.add_edge("brief_generation", "dev_auto_approve")
        builder.add_edge("dev_auto_approve", "notification_dispatch")

    builder.add_edge("notification_dispatch", "case_persistence")
    builder.add_edge("case_persistence", "response")
    builder.add_edge("response", END)

    # ==========================================
    # 3. DURABLE STATE COMPILATION
    # ==========================================
    # ✅ INJECTED: Uses the platform singleton checkpointer from the container
    # ✅ PROTECTED: Forces an explicit checkpoint state split right before human_review executes
    logger.info("Compiling escalation orchestration workflow with shared Postgres checkpointer...")
    app = builder.compile(
        checkpointer=container.checkpointer,
        interrupt_before=["human_review"] if enable_hitl else None
    )

    return app