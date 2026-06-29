import os
import logging
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langgraph.graph import StateGraph, END

# ❌ REMOVED: MemorySaver import

# DB & Schemas
from layer_2_account_agent.schemas.account_state import AccountState
from layer_2_account_agent.schemas.domain import ActionType, SubclassificationResult

# Nodes
from layer_2_account_agent.nodes.validate_contract_node import validate_contract
from layer_2_account_agent.nodes.subclassify_issue_node import subclassify_issue
from layer_2_account_agent.nodes.clarification_check_node import clarification_check
from layer_2_account_agent.nodes.identity_resolution_node import identity_resolution
from layer_2_account_agent.nodes.fetch_account_context_node import fetch_account_context
from layer_2_account_agent.nodes.abuse_guard_node import abuse_guard
from layer_2_account_agent.nodes.action_resolution_node import action_resolution_node 
from layer_2_account_agent.nodes.takeover_detection_node import takeover_detection
from layer_2_account_agent.nodes.risk_assessment_node import risk_assessment
from layer_2_account_agent.nodes.verification_policy_node import verification_policy
from layer_2_account_agent.nodes.idempotency_node import idempotency
from layer_2_account_agent.nodes.password_reset_node import password_reset
from layer_2_account_agent.nodes.unlock_account_node import unlock_account
from layer_2_account_agent.nodes.invoice_retrieval_node import invoice_retrieval
from layer_2_account_agent.nodes.billing_history_node import billing_history
from layer_2_account_agent.nodes.security_escalation_node import get_security_escalation_node
from layer_2_account_agent.nodes.audit_log_node import audit_log
from layer_2_account_agent.nodes.response_generation_node import response_generation_node

# Routers
from layer_2_account_agent.routers.decision_router import clarification_router, execution_router

logger = logging.getLogger(__name__)

# GRAPH FACTORY
def build_account_graph(container):
    """
    Build Account Agent LangGraph workflow using Dependency Injection.
    """
    logger.info("Building Account graph with injected dependencies...")
    
    builder = StateGraph(AccountState)

    # ==========================================
    # CORE NODES (Using container injections)
    # ==========================================
    builder.add_node("validate_contract", validate_contract)

    builder.add_node(
        "subclassify_issue",
        lambda state: subclassify_issue(
            state,
            container.subclassifier
        )
    )

    builder.add_node("clarification_check", clarification_check)

    builder.add_node(
        "identity_resolution",
        lambda state: identity_resolution(
            state,
            container.identity_service
        )
    )

    builder.add_node(
        "fetch_account_context",
        lambda state: fetch_account_context(
            state,
            container.account_repo,
            container.billing_repo
        )
    )

    builder.add_node(
        "abuse_guard",
        lambda state: abuse_guard(
            state,
            container.abuse_guard
        )
    )

    builder.add_node("action_resolution", action_resolution_node)
    builder.add_node("takeover_detection", takeover_detection)
    builder.add_node("risk_assessment", risk_assessment)
    builder.add_node("verification_policy", verification_policy)

    builder.add_node(
        "idempotency",
        lambda state: idempotency(
            state,
            container.idempotency_service
        )
    )

    # ==========================================
    # EXECUTION NODES
    # ==========================================
    builder.add_node(
        "password_reset",
        lambda state: password_reset(
            state,
            container.auth_provider,
            container.idempotency_service
        )
    )

    builder.add_node(
        "unlock_account",
        lambda state: unlock_account(
            state,
            container.auth_provider,
            container.idempotency_service
        )
    )

    builder.add_node(
        "invoice_retrieval",
        lambda state: invoice_retrieval(
            state,
            container.billing_repo,
            container.idempotency_service
        )
    )

    builder.add_node(
        "billing_history",
        lambda state: billing_history(
            state,
            container.billing_repo,
            container.idempotency_service
        )
    )

    builder.add_node(
        "security_escalation",
        get_security_escalation_node(
            auth_provider=container.auth_provider,
            audit_repo=container.security_repo,
            idempotency_service=container.idempotency_service
        )
    )

    # ==========================================
    # FINAL NODES
    # ==========================================
    builder.add_node(
        "audit_log",
        lambda state: audit_log(
            state,
            container.security_repo
        )
    )

    builder.add_node("response_generation", response_generation_node)

    # ==========================================
    # EDGES
    # ==========================================
    builder.set_entry_point("validate_contract")

    builder.add_edge("validate_contract", "subclassify_issue")
    builder.add_edge("subclassify_issue", "clarification_check")
    builder.add_conditional_edges("clarification_check", clarification_router)
    builder.add_edge("identity_resolution", "fetch_account_context")
    builder.add_edge("fetch_account_context", "abuse_guard")
    builder.add_edge("abuse_guard", "action_resolution")
    builder.add_edge("action_resolution", "takeover_detection")
    builder.add_edge("takeover_detection", "risk_assessment")
    builder.add_edge("risk_assessment", "verification_policy")
    builder.add_edge("verification_policy", "idempotency")
    
    builder.add_conditional_edges("idempotency", execution_router)

    # Execution → Audit
    builder.add_edge("password_reset", "audit_log")
    builder.add_edge("unlock_account", "audit_log")
    builder.add_edge("invoice_retrieval", "audit_log")
    builder.add_edge("billing_history", "audit_log")
    builder.add_edge("security_escalation", "audit_log")

    # Final response
    builder.add_edge("audit_log", "response_generation")
    builder.add_edge("response_generation", END)

    # ==========================================
    # DURABLE STATE COMPILATION
    # ==========================================
    # ✅ INJECTED: Uses the central platform singleton checkpointer passed in from the container
    logger.info("Compiling Account workflow with shared Postgres checkpointer...")
    return builder.compile(checkpointer=container.checkpointer)