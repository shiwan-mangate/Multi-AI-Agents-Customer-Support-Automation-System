from datetime import datetime, UTC
from typing import Dict, Any

from layer_2_proactive_agent.schemas.proactive_state import ProactiveState
from layer_2_proactive_agent.services.escalation_service import EscalationService
from layer_2_proactive_agent.services.suppression_service import SuppressionService
from layer_2_proactive_agent.repositories.proactive_outreach_repository import ProactiveOutreachRepository
from layer_2_proactive_agent.database.session import SessionLocal
from layer_2_proactive_agent.utils.logger import logger

# Initialize the stateless escalation service once
escalation_service = EscalationService()


def escalation_handoff_node(state: ProactiveState) -> Dict[str, Any]:
    """
    Packages the customer context for human supervisor review (Layer 3)
    and registers the escalation in the suppression registry database.

    Verified against DB constraints:
    - customer_id -> bigint (int)
    - workflow_id/signal_id/ticket_id -> character varying (str)
    """
    workflow_id = state["workflow_id"]
    customer_profile = state["customer_profile"]
    signal_assessment = state["signal_assessment"]
    risk_assessment = state["risk_assessment"]
    signal = state["signal"]
    decision = state["decision"]

    logger.info(
        "Status=START | Node=ESCALATION_HANDOFF | Workflow=%s",
        workflow_id,
    )

    timestamp = datetime.now(UTC).isoformat()

    try:
        missing_context = []
        if customer_profile is None:
            missing_context.append("customer_profile")
        if signal_assessment is None:
            missing_context.append("signal_assessment")
        if risk_assessment is None:
            missing_context.append("risk_assessment")
        if decision is None:
            missing_context.append("decision")

        if missing_context:
            raise ValueError(
                f"Missing required context for escalation handoff: {', '.join(missing_context)}"
            )

        # 1. Package the Escalation Ticket (Full Signature)
        handoff = escalation_service.handoff(
            workflow_id=workflow_id,
            customer_profile=customer_profile,
            signal_assessment=signal_assessment,
            risk_assessment=risk_assessment,
        )

        # 2. Persist the Escalation to the Registry with safe transaction handling
        with SessionLocal() as db:
            try:
                repo = ProactiveOutreachRepository(session=db)
                suppression_service = SuppressionService(repo=repo)
                
                # Defensive guard to extract action whether it is an Enum object or a raw string literal
                action_obj = getattr(decision, "action", None)
                action_value = action_obj.value if hasattr(action_obj, "value") else str(action_obj)

                record = suppression_service.create_outreach_record(
                    workflow_id=workflow_id,
                    signal_id=signal.signal_id,
                    customer_id=signal.customer_id,
                    signal_type=signal.signal_type,
                    decision=action_value,
                )
                suppression_service.save_outreach(record)
                db.commit()
            except Exception:
                db.rollback()  # Prevent dirty session states on database failure
                raise

        logger.info(
            "Status=SUCCESS | Node=ESCALATION_HANDOFF | Workflow=%s | TicketID=%s",
            workflow_id,
            handoff.ticket_id,
        )

        return {
            "escalation_handoff": handoff,
            "current_node": "escalation_handoff_node",
            "workflow_logs": [
                {
                    "timestamp": timestamp,
                    "node": "escalation_handoff_node",
                    "message": f"Escalation package created (Ticket: {handoff.ticket_id}) and recorded in registry.",
                }
            ],
        }

    except Exception as exc:
        logger.exception(
            "Status=FAILED | Node=ESCALATION_HANDOFF | Workflow=%s | Error=%s",
            workflow_id,
            str(exc),
        )
        raise