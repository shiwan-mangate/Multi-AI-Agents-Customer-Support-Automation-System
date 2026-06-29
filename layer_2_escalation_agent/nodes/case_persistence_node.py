import logging
from datetime import datetime, UTC

from layer_2_escalation_agent.schemas.escalation_state import EscalationState
from layer_2_escalation_agent.schemas.audit_record import AuditEventType, OperatorType
from layer_2_escalation_agent.repositories.escalation_repository import EscalationRepository
from layer_2_escalation_agent.repositories.audit_repository import AuditRepository
from layer_2_escalation_agent.repositories.notification_outbox_repository import NotificationOutboxRepository
from layer_2_escalation_agent.db.session import get_db
from layer_2_escalation_agent.schemas.human_decision import (
    HumanDecision,
    HumanDecisionType,
)
logger = logging.getLogger(__name__)


def case_persistence_node(
    state: EscalationState,
    escalation_repo=None,
    audit_repo=None,
    notification_outbox_repo=None
) -> EscalationState:
    """
    Persist authoritative escalation state atomically.
    Acts as the transactional coordinator (Unit of Work) for repositories.
    
    Supports clean Dependency Injection from the global orchestration container 
    with defensive session management to prevent downstream pipeline crashes.
    """
    logger.info("Executing case_persistence_node")

    state["current_node"] = "case_persistence_node"

    case_id = state["case_id"]
    ticket_id = state["ticket_id"]
    customer_id = state["customer_id"]

    trigger_assessment = state["trigger_assessment"]
    risk_assessment = state["risk_assessment"]
    routing_decision = state["routing_decision"]
    human_brief = state["human_brief"]
    notification_jobs = state["notification_jobs"]
    holding_message = state.get("holding_message")
    source_agent = state["source_agent"]
    human_decision = state.get("human_decision")

    if isinstance(human_decision, dict):
        try:
            decision_value = human_decision.get("decision")

            if isinstance(decision_value, str):
                human_decision["decision"] = HumanDecisionType(
                    decision_value.lower()
                )

            human_decision = HumanDecision(**human_decision)

        except Exception as exc:
            raise ValueError(
                f"Invalid human_decision payload: {exc}"
            )

    if not notification_jobs:
        error_msg = "Persistence blocked: notification_jobs empty."
        logger.error(error_msg)
        state["errors"].append(error_msg)
        raise ValueError(error_msg)

    session = None
    db_generator = None
    is_container_session = escalation_repo is not None

    try:
        # 1. Resolve Repositories and Session Context
        if is_container_session:
            # Container-optimized path using shared master DB session
            esc_repo = escalation_repo
            active_audit_repo = audit_repo
            active_outbox_repo = notification_outbox_repo
            session = getattr(esc_repo, "db", None) or getattr(esc_repo, "session", None)
        else:
            # Standalone legacy fallback execution context path
            db_generator = get_db()
            session = next(db_generator)
            esc_repo = EscalationRepository(session)
            active_audit_repo = AuditRepository(session)
            active_outbox_repo = NotificationOutboxRepository(session)

        # 2. Write Core Escalation Case
        esc_repo.create_case(
            case_id=case_id,
            ticket_id=ticket_id,
            customer_id=customer_id,
            source_agent=source_agent,
            trigger_assessment=trigger_assessment.model_dump() if hasattr(trigger_assessment, "model_dump") else trigger_assessment,
            risk_assessment=risk_assessment.model_dump() if hasattr(risk_assessment, "model_dump") else risk_assessment,
            human_brief=human_brief.model_dump() if hasattr(human_brief, "model_dump") else human_brief,
            routing_decision=routing_decision.model_dump() if hasattr(routing_decision, "model_dump") else routing_decision,
            holding_message=holding_message,
        )

        # 3. Stage Fanout Notifications into Outbox
        for job in notification_jobs:
            active_outbox_repo.enqueue_job(job)

        # 4. Log Architectural Audit Trails
        decision_val = "PENDING_HUMAN_REVIEW"
        if human_decision:
            decision_val = human_decision.decision.value if hasattr(human_decision.decision, "value") else str(human_decision.decision)

        active_audit_repo.log_event(
            case_id=case_id,
            ticket_id=ticket_id,
            event_type=AuditEventType.ROUTING_COMPLETED,
            payload={
                "team": routing_decision.assigned_team if hasattr(routing_decision, "assigned_team") else routing_decision.get("assigned_team"),
                "status": decision_val,
            },
            operator_type=OperatorType.AI,
        )

        active_audit_repo.log_event(
            case_id=case_id,
            ticket_id=ticket_id,
            event_type=AuditEventType.NOTIFICATION_ENQUEUED,
            payload={
                "job_count": len(notification_jobs),
            },
            operator_type=OperatorType.SYSTEM,
        )

        # 5. Atomic Unit Commit Boundary
        if session:
            try:
                session.commit()
            except Exception:
                session.rollback()
                raise

        state["audit_status"] = "persisted"
        state["holding_sent"] = True

        state["workflow_logs"].append({
            "node": "case_persistence_node",
            "timestamp": datetime.now(UTC).isoformat(),
            "message": "Escalation persisted successfully.",
            "data": {
                "case_id": case_id,
                "notification_jobs": len(notification_jobs),
            },
        })

        logger.info(
            "Persistence complete | ticket_id=%s | case_id=%s",
            ticket_id,
            case_id,
        )

    except Exception as exc:
        if session:
            session.rollback()
        state["audit_status"] = "failed"
        error_msg = f"Persistence transaction failed | {str(exc)}"
        logger.error(error_msg)
        state["errors"].append(error_msg)
        raise ValueError(error_msg)

    finally:
        if not is_container_session and session:
            session.close()
            
        if db_generator:
            try:
                next(db_generator)
            except StopIteration:
                pass

    return state