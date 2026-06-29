import logging
import uuid
from typing import Dict, Any, Optional
from typing import Any

from langgraph.types import Command
from typing import Any, Dict, Optional, List

# Import the graph builder function you created in graph/orchestrator.py
from layer_2_escalation_agent.graph.escalation_graph import build_escalation_graph
from layer_2_escalation_agent.factories.state_factory import EscalationStateFactory

logger = logging.getLogger("QA_Engine")

# Allowed entry point callers boundary matching your factory configuration
ALLOWED_SOURCE_AGENTS = {
    "triage_agent",
    "faq_agent",
    "refund_agent",
    "account_agent",
    "tech_ops_agent",
    "supervisor",
    "system"
}

# Lazy Singleton Graph instantiation to prevent costly recompilations
_GRAPH = None

def get_escalation_graph():
    global _GRAPH
    if _GRAPH is None:
        logger.info("Compiling orchestration graph engine...")
        _GRAPH = build_escalation_graph(enable_hitl=True)
    return _GRAPH


def _build_config(thread_id: Optional[str] = None) -> Dict[str, Any]:
    """Build LangGraph execution context configuration with persistent Thread IDs."""
    return {
        "configurable": {
            "thread_id": thread_id or f"esc-{uuid.uuid4().hex[:12]}"
        }
    }


def _serialize_final_state(final_state: Dict[str, Any], thread_id: str) -> Dict[str, Any]:
    """Convert internal Graph dict state structures into clean JSON-serializable responses."""
    response = final_state.get("response")
    if response is None:
        raise ValueError("Workflow finished execution without building a valid EscalationResponse object.")

    return {
        "status": response.status.value if hasattr(response.status, "value") else str(response.status),
        "thread_id": thread_id,
        "case_id": final_state.get("case_id"),
        "response": response.model_dump(mode="json", by_alias=True) if hasattr(response, "model_dump") else response,
        "workflow_logs": final_state.get("workflow_logs", []),
    }


# =====================================================================
# PUBLIC AGENT INTERFACE API EXPORTS
# =====================================================================

def run_escalation_agent(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Primary interface gateway to kick off an escalation sequence from any upstream agent.
    """
    graph = get_escalation_graph()
    ticket_id = str(payload.get("ticket_id") or "").strip()
    source_agent = str(payload.get("source_agent", "system")).strip().lower()

    try:
        if source_agent not in ALLOWED_SOURCE_AGENTS:
            raise ValueError(f"Unauthorized source agent request signature: {source_agent}")

        # Hydrate internal schema states using our factory module
        state = EscalationStateFactory.from_payload(payload)
        config = _build_config()
        thread_id = config["configurable"]["thread_id"]

        final_state = None
        # Stream workflow state transformations across the graph topology step-by-step
        for event in graph.stream(state, config=config, stream_mode="values"):
            final_state = event

        # Check snapshot records to see if a node triggered an interrupt state loop suspension
        snapshot = graph.get_state(config)
        if snapshot and snapshot.tasks:
            for task in snapshot.tasks:
                if getattr(task, "interrupts", None):
                    return {
                        "status": "HUMAN_REVIEW_REQUIRED",
                        "thread_id": thread_id,
                        "ticket_id": ticket_id,
                        "case_id": final_state.get("case_id") if final_state else None,
                        "source_agent": source_agent,
                        "review_payload": task.interrupts[0].value,
                        "workflow_logs": final_state.get("workflow_logs", []) if final_state else [],
                    }

        if final_state is None:
            raise ValueError("State stream execution yielded an empty context dictionary frame.")

        return _serialize_final_state(final_state, thread_id)

    except Exception as exc:
        logger.exception(f"Escalation runner caught an execution breakdown target thread: {exc}")
        return {
            "status": "FAILED",
            "ticket_id": ticket_id,
            "source_agent": source_agent,
            "error": str(exc),
        }


def resume_escalation_review(thread_id: str, decision: Dict[str, Any]) -> Dict[str, Any]:
    """
    Resumes a paused human-in-the-loop state suspension by feeding human commands back into the graph.
    """
    graph = get_escalation_graph()
    try:
        config = _build_config(thread_id)
        final_state = None

        # Inject the human decision dictionary straight back into the graph checkpoint via a resume Command
        for event in graph.stream(Command(resume=decision), config=config, stream_mode="values"):
            final_state = event

        if final_state is None:
            raise ValueError("Resume transaction pipeline produced no readable final output frame.")

        return _serialize_final_state(final_state, thread_id)

    except Exception as exc:
        logger.exception(f"Failed to cleanly resume human review thread instance {thread_id}: {exc}")
        return {
            "status": "FAILED",
            "thread_id": thread_id,
            "error": str(exc),
        }