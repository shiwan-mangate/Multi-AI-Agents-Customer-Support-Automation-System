import logging
import uuid
from typing import Dict, Any, Optional

from langgraph.types import Command

from layer_2_escalation_agent.graph.escalation_graph import build_escalation_graph
from layer_2_escalation_agent.factories.state_factory import EscalationStateFactory

logger = logging.getLogger(__name__)


# =========================================================
# ALLOWED UPSTREAM CALLERS
# =========================================================

ALLOWED_SOURCE_AGENTS = {
    "triage_agent",
    "faq_agent",
    "refund_agent",
    "account_agent",
    "tech_bug_agent",
    "supervisor",
}


# =========================================================
# SINGLETON GRAPH
# =========================================================

_GRAPH = None


def get_escalation_graph():
    """
    Lazy singleton graph compilation.

    Prevents expensive LangGraph recompilation
    on every escalation request.
    """
    global _GRAPH

    if _GRAPH is None:
        logger.info("Compiling escalation agent graph...")
        _GRAPH = build_escalation_graph()

    return _GRAPH


# =========================================================
# CONFIG BUILDER
# =========================================================

def _build_config(thread_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Build LangGraph execution config.

    Required because MemorySaver checkpointing
    requires configurable thread_id.
    """
    return {
        "configurable": {
            "thread_id": thread_id or f"esc-{uuid.uuid4().hex}"
        }
    }


# =========================================================
# RESPONSE SERIALIZER
# =========================================================

def _serialize_final_state(
    final_state: Dict[str, Any],
    thread_id: str
) -> Dict[str, Any]:
    """
    Convert internal workflow state into clean public API response.
    """

    response = final_state.get("response")

    if response is None:
        raise ValueError("Escalation workflow completed without response.")

    return {
        "status": (
            response.status.value
            if hasattr(response.status, "value")
            else str(response.status)
        ),
        "thread_id": thread_id,
        "case_id": final_state.get("case_id"),
        "response": (
            response.model_dump(mode="json")
            if hasattr(response, "model_dump")
            else response
        ),
        "workflow_logs": final_state.get("workflow_logs", []),
    }


# =========================================================
# INTERRUPT DETECTION
# =========================================================

def _extract_interrupt_payload(graph, config) -> Optional[Dict[str, Any]]:
    """
    Detect if workflow paused on a LangGraph interrupt()
    and safely extract the review payload.
    """

    snapshot = graph.get_state(config)

    if not snapshot or not snapshot.tasks:
        return None

    for task in snapshot.tasks:
        if getattr(task, "interrupts", None):
            if task.interrupts:
                return task.interrupts[0].value

    return None


# =========================================================
# MAIN ENTRYPOINT
# =========================================================

def run_escalation_agent(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Execute escalation workflow.

    Accepted upstream callers:
    - triage_agent
    - faq_agent
    - refund_agent
    - account_agent
    - tech_bug_agent
    - supervisor

    Returns:
    - ESCALATED
    - DUPLICATE_SUPPRESSED
    - HUMAN_REVIEW_REQUIRED
    - FAILED
    """

    graph = get_escalation_graph()

    ticket_id = payload.get("ticket_id")
    source_agent = payload.get("source_agent", "unknown")

    logger.info(
        "Escalation request received | ticket_id=%s | source_agent=%s",
        ticket_id,
        source_agent,
    )

    try:
        # -------------------------------------------------
        # SOURCE VALIDATION
        # -------------------------------------------------
        if source_agent not in ALLOWED_SOURCE_AGENTS:
            raise ValueError(
                f"Unauthorized escalation source_agent: {source_agent}"
            )

        # -------------------------------------------------
        # STATE HYDRATION
        # -------------------------------------------------
        state = EscalationStateFactory.from_payload(payload)

        config = _build_config()
        thread_id = config["configurable"]["thread_id"]

        final_state = None

        # -------------------------------------------------
        # GRAPH EXECUTION
        # -------------------------------------------------
        for event in graph.stream(
            state,
            config=config,
            stream_mode="values"
        ):
            final_state = event

        # -------------------------------------------------
        # HUMAN REVIEW INTERRUPT
        # -------------------------------------------------
        interrupt_payload = _extract_interrupt_payload(graph, config)

        if interrupt_payload:
            logger.info(
                "Escalation paused for human review | ticket_id=%s | thread_id=%s",
                ticket_id,
                thread_id,
            )

            return {
                "status": "HUMAN_REVIEW_REQUIRED",
                "thread_id": thread_id,
                "ticket_id": ticket_id,
                "case_id": (
                    final_state.get("case_id")
                    if final_state
                    else None
                ),
                "source_agent": source_agent,
                "review_payload": interrupt_payload,
                "workflow_logs": (
                    final_state.get("workflow_logs", [])
                    if final_state
                    else []
                ),
            }

        # -------------------------------------------------
        # NORMAL COMPLETION
        # -------------------------------------------------
        if final_state is None:
            raise ValueError("Escalation workflow produced no state.")

        logger.info(
            "Escalation completed successfully | ticket_id=%s",
            ticket_id,
        )

        return _serialize_final_state(final_state, thread_id)

    except Exception as exc:
        logger.exception(
            "Escalation agent execution failed | ticket_id=%s",
            ticket_id,
        )

        return {
            "status": "FAILED",
            "ticket_id": ticket_id,
            "source_agent": source_agent,
            "error": str(exc),
        }


# =========================================================
# HUMAN REVIEW RESUME
# =========================================================

def resume_escalation_review(
    thread_id: str,
    decision: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Resume paused escalation after human governance decision.

    Approve:
    {
        "decision": "approve",
        "reviewer_id": "legal_director",
        "notes": "Approved"
    }

    Override:
    {
        "decision": "override",
        "reviewer_id": "ops_manager",
        "override_team": "legal_team",
        "notes": "Route to legal"
    }

    Reject:
    {
        "decision": "reject",
        "reviewer_id": "security_lead",
        "notes": "Rejected"
    }
    """

    graph = get_escalation_graph()

    logger.info(
        "Resuming escalation review | thread_id=%s",
        thread_id,
    )

    try:
        config = _build_config(thread_id)

        final_state = None

        for event in graph.stream(
            Command(resume=decision),
            config=config,
            stream_mode="values"
        ):
            final_state = event

        if final_state is None:
            raise ValueError("Resume workflow produced no final state.")

        logger.info(
            "Escalation resume completed | thread_id=%s",
            thread_id,
        )

        return _serialize_final_state(final_state, thread_id)

    except Exception as exc:
        logger.exception(
            "Escalation resume failed | thread_id=%s",
            thread_id,
        )

        return {
            "status": "FAILED",
            "thread_id": thread_id,
            "error": str(exc),
        }