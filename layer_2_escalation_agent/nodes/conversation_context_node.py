import logging
from datetime import datetime, UTC
from typing import Dict, Any, List

from layer_2_escalation_agent.schemas.escalation_state import EscalationState
from layer_2_escalation_agent.schemas.conversation_context import (
    ConversationContext,
    FailureReason,
)
from layer_2_escalation_agent.repositories.conversation_repository import ConversationRepository
from layer_2_escalation_agent.db.session import get_db

logger = logging.getLogger(__name__)


def conversation_context_node(
    state: EscalationState,
    conversation_repo=None
) -> EscalationState:
    """
    Assemble escalation conversation evidence context.

    Supports clean Dependency Injection from the global orchestrator container 
    with a seamless legacy session lifecycle fallback.
    """
    logger.info("Executing conversation_context_node")

    state["current_node"] = "conversation_context_node"

    ticket_id = state["ticket_id"]
    source_agent = state["source_agent"]
    workflow_logs = state["workflow_logs"]
    ticket = state["ticket"]

    message = (
        ticket.get("message_english")
        or ticket.get("message_raw")
        or ""
    )

    transcript = (
        f"Customer [Ticket {ticket_id}]: {message}\n"
        "[System fallback transcript]"
    )

    agent_actions = []
    knowledge_gap_detected = False

    failure_reasons = _extract_failure_reasons(workflow_logs)

    if "knowledge_gap_detected" in failure_reasons:
        knowledge_gap_detected = True

    session = None
    db_generator = None

    try:
        # 1. Resolve Dependency Providers context
        if conversation_repo is not None:
            # Container-optimized path using shared master DB session
            repo = conversation_repo
        else:
            # Standalone legacy execution path
            db_generator = get_db()
            session = next(db_generator)
            repo = ConversationRepository(session)

        # 2. Execute Action & Transcript Mapping
        transcript = repo.build_conversation_transcript(
            ticket_id=ticket_id,
            current_message=message,
            workflow_logs=workflow_logs,
        )

        agent_actions = repo.extract_agent_actions(
            workflow_logs=workflow_logs,
            source_agent=source_agent,
        )

        logger.info(
            "Conversation context assembled | ticket_id=%s | actions=%d | failures=%d",
            ticket_id,
            len(agent_actions),
            len(failure_reasons),
        )

    except Exception as exc:
        logger.error(
            "Conversation context degraded | ticket_id=%s | error=%s",
            ticket_id,
            str(exc),
        )

    finally:
        # 3. Clean fallback connection lifecycle management
        if session:
            session.close()
        if db_generator:
            try:
                next(db_generator)
            except StopIteration:
                pass

    # 4. Assemble State payload contracts
    context = ConversationContext(
        conversation_transcript=transcript,
        agent_actions_taken=agent_actions,
        failure_reasons=failure_reasons,
        knowledge_gap_detected=knowledge_gap_detected,
    )

    state["conversation_context"] = context

    log_entry = {
        "node": "conversation_context_node",
        "timestamp": datetime.now(UTC).isoformat(),
        "message": "Conversation evidence context assembled.",
        "data": {
            "actions_extracted": len(agent_actions),
            "failure_reasons": failure_reasons,
            "knowledge_gap_detected": knowledge_gap_detected,
        },
    }

    state["workflow_logs"].append(log_entry)

    return state


def _extract_failure_reasons(
    workflow_logs: List[Dict[str, Any]]
) -> List[str]:
    """
    Deterministic failure intelligence extraction.
    Returns string literals to guarantee clean validation array boundaries.
    """
    failures = set()

    for log in workflow_logs:
        msg = str(log.get("message", "")).lower()
        data = str(log.get("data", "")).lower()
        combined = f"{msg} {data}"

        if (
            "retrieval failed" in combined
            or "no chunks" in combined
            or "knowledge unavailable" in combined
        ):
            failures.add(FailureReason.KNOWLEDGE_GAP_DETECTED.value)
            continue

        if (
            "manual review" in combined
            or "human review" in combined
            or "approval required" in combined
        ):
            failures.add(FailureReason.MANUAL_REVIEW_REQUIRED.value)
            continue

        if (
            "verification failed" in combined
            or "authentication failure" in combined
        ):
            failures.add(FailureReason.IDENTITY_VERIFICATION_FAILED.value)
            continue

        if (
            "policy denied" in combined
            or "not eligible" in combined
            or "policy blocked" in combined
        ):
            failures.add(FailureReason.POLICY_CONFLICT.value)
            continue

        if (
            "confidence" in combined
            or "threshold" in combined
        ):
            failures.add(FailureReason.LOW_CONFIDENCE.value)
            continue

        if (
            "failed" in combined
            or "error" in combined
            or "timeout" in combined
        ):
            failures.add(FailureReason.MANUAL_REVIEW_REQUIRED.value)

    return list(failures)