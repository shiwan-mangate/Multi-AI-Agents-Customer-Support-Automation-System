import logging
from datetime import datetime, UTC

from layer_2_escalation_agent.schemas.escalation_state import EscalationState
from layer_2_escalation_agent.services.trigger_engine import TriggerEngine
from layer_2_escalation_agent.repositories.escalation_repository import EscalationRepository
from layer_2_escalation_agent.db.session import get_db

logger = logging.getLogger(__name__)


def trigger_assessment_node(
    state: EscalationState, 
    trigger_engine=None, 
    escalation_repo=None
) -> EscalationState:
    """
    Determine escalation trigger intelligence and detect active duplicates.
    Supports clean Dependency Injection from global orchestrator container with 
    legacy structural fallbacks.
    """
    logger.info("Executing trigger_assessment_node")

    state["current_node"] = "trigger_assessment_node"

    ticket_id = state["ticket_id"]
    customer_id = state["customer_id"]
    source_agent = state["source_agent"]
    workflow_logs = state["workflow_logs"]
    sentiment = state["initial_sentiment"]

    ticket = state["ticket"]

    message = (
        ticket.get("message_english")
        or ticket.get("message_raw")
        or ""
    )

   
    engine = trigger_engine or TriggerEngine()
    
    logger.warning(
    "TRIGGER INPUT | repeat_issue_count=%s | knowledge_gap=%s",
    state.get("repeat_issue_count"),
    state.get("knowledge_gap_detected")
)

    assessment = engine.assess(
    message=message,
    sentiment=sentiment,
    source_agent=source_agent,
    workflow_logs=workflow_logs,
    knowledge_gap_detected=state.get(
        "knowledge_gap_detected",
        False
    ),
    repeat_issue_count=state.get(
        "repeat_issue_count",
        0
    ),
)

    category_str = assessment.category.value if hasattr(assessment.category, "value") else str(assessment.category)

    logger.info(
        "Trigger classification complete | ticket_id=%s | category=%s",
        ticket_id,
        category_str,
    )

    if escalation_repo is not None:
    
        try:
            duplicate_case = escalation_repo.find_active_duplicate_case(
                ticket_id=ticket_id,
                customer_id=customer_id,
            )

            if duplicate_case:
                assessment.duplicate_case_detected = True
                assessment.existing_case_id = duplicate_case["case_id"]

                logger.warning(
                    "Duplicate escalation detected | ticket_id=%s | case_id=%s",
                    ticket_id,
                    duplicate_case["case_id"],
                )
        except Exception as exc:
            logger.error(
                "Duplicate detection degraded (injected repo) | ticket_id=%s | error=%s",
                ticket_id,
                str(exc),
            )
            assessment.duplicate_case_detected = False
            assessment.existing_case_id = None
    else:
        # Standalone legacy fallback execution context path
        db_generator = get_db()
        session = None
        try:
            session = next(db_generator)
            fallback_repo = EscalationRepository(session)

            duplicate_case = fallback_repo.find_active_duplicate_case(
                ticket_id=ticket_id,
                customer_id=customer_id,
            )

            if duplicate_case:
                assessment.duplicate_case_detected = True
                assessment.existing_case_id = duplicate_case["case_id"]

                logger.warning(
                    "Duplicate escalation detected | ticket_id=%s | case_id=%s",
                    ticket_id,
                    duplicate_case["case_id"],
                )

        except Exception as exc:
            logger.error(
                "Duplicate detection degraded (standalone fallback) | ticket_id=%s | error=%s",
                ticket_id,
                str(exc),
            )
            assessment.duplicate_case_detected = False
            assessment.existing_case_id = None

        finally:
            if session:
                session.close()
            try:
                next(db_generator)
            except StopIteration:
                pass

    state["trigger_assessment"] = assessment


    reasons_list = [
        r.value if hasattr(r, "value") else str(r) 
        for r in assessment.reasons
    ]

    log_entry = {
        "node": "trigger_assessment_node",
        "timestamp": datetime.now(UTC).isoformat(),
        "message": "Escalation trigger intelligence completed.",
        "data": {
            "category": category_str,
            "reasons": reasons_list,
            "duplicate_case_detected": assessment.duplicate_case_detected,
            "existing_case_id": assessment.existing_case_id,
        },
    }

    state["workflow_logs"].append(log_entry)

    return state