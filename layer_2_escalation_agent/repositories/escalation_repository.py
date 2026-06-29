import logging
from typing import Dict, Any, Optional

from sqlalchemy.orm import Session
from sqlalchemy import func

# Importing the exact EscalationCase model we just verified
from layer_2_escalation_agent.db.model.escalation_cases_model import EscalationCase

logger = logging.getLogger(__name__)

# Updated to remain completely uniform with your operational status states
VALID_CASE_STATUSES = {
    "open",
    "in_review",
    "resolved",
    "closed",
    "ESCALATED",
    "DUPLICATE_SUPPRESSED",
    "FAILED"
}

class EscalationRepository:
    """
    Repository for escalation case persistence.
    
    Note: Does NOT manage its own transaction commits or rollbacks.
    The calling orchestrator/node manages the transaction lifecycle 
    atomically across multiple tables.
    """

    def __init__(self, session: Session):
        self.session = session

    def _execute_update(
        self,
        query,
        update_values: Dict[str, Any],
        error_message: str
    ) -> bool:
        """
        Execute UPDATE safely within the shared parent transaction.
        Let exceptions bubble up so the orchestrator can roll back cleanly.
        """
        try:
            rowcount = query.update(update_values, synchronize_session=False)
            
            if rowcount == 0:
                logger.warning("%s | No rows affected.", error_message)
                return False
                
            # Explicitly flush to push the mutation to the database to catch
            # constraint violations immediately without committing the transaction.
            self.session.flush()
            return True
            
        except Exception as exc:
            logger.error("%s | Error: %s", error_message, str(exc))
            raise

    def _base_query(self):
        """Helper to ensure consistent SELECT * dictionary returns."""
        return self.session.query(*EscalationCase.__table__.columns)

    def create_case(
        self,
        case_id: str,
        ticket_id: str,
        customer_id: int,
        source_agent: str,
        trigger_assessment: dict,
        risk_assessment: dict,
        human_brief: dict,
        routing_decision: dict,
        holding_message: str = None,
    ):
        """
        Persist the case mutation payload.
        """
        # Force uppercase to satisfy the PostgreSQL CHECK constraint
        raw_risk_level = risk_assessment.get("level", "low")
        db_risk_level = str(raw_risk_level).strip().upper() 

        try:
            # Standard ORM instantiation. JSONB naturally handles dict/list payloads.
            new_case = EscalationCase(
                case_id=case_id,
                ticket_id=ticket_id,
                customer_id=customer_id,
                source_agent=source_agent,
                trigger_category=trigger_assessment.get("category", "general"),
                trigger_reasons=trigger_assessment.get("reasons", []),
                risk_score=risk_assessment.get("score", 0.0),
                risk_level=db_risk_level, 
                assigned_team=routing_decision.get("assigned_team", "general_support_team"),
                status="open",
                holding_sent=True if holding_message else False,
                holding_message=holding_message,
                human_brief=human_brief,
                recommended_action=human_brief.get("recommended_next_action", "Investigate and resolve case"),
                sla_deadline=routing_decision.get("sla_deadline"),
                duplicate_of_case_id=None
            )

            self.session.add(new_case)
            
            # Flush to immediately execute the INSERT within the current transaction
            self.session.flush()
            return True

        except Exception as exc:
            logger.error("Failed to create escalation case row record for case_id=%s | Error: %s", case_id, str(exc))
            raise

    def find_active_duplicate_case(
        self,
        ticket_id: str, 
        customer_id: int
    ) -> Optional[Dict[str, Any]]:
        """
        Find unresolved escalation for ticket/customer pair.
        """
        try:
            result = self._base_query().filter(
                EscalationCase.ticket_id == str(ticket_id),
                EscalationCase.customer_id == customer_id,
                EscalationCase.status.in_(['open', 'in_review', 'ESCALATED'])
            ).order_by(
                EscalationCase.created_at.desc()
            ).first()

            return result._asdict() if result else None

        except Exception:
            logger.exception(
                "Failed duplicate lookup ticket_id=%s customer_id=%s",
                ticket_id,
                customer_id,
            )
            return None

    def get_case(self, case_id: str) -> Optional[Dict[str, Any]]:
        """
        Fetch escalation case.
        """
        try:
            result = self._base_query().filter(
                EscalationCase.case_id == case_id
            ).first()

            return result._asdict() if result else None

        except Exception:
            logger.exception(
                "Failed fetching escalation case case_id=%s",
                case_id
            )
            return None

    def update_case_status(
        self,
        case_id: str,
        new_status: str
    ) -> bool:
        """
        Update escalation lifecycle state.
        """
        if new_status not in VALID_CASE_STATUSES:
            raise ValueError(f"Invalid case status: {new_status}")

        query = self.session.query(EscalationCase).filter(
            EscalationCase.case_id == case_id
        )
        
        update_values = {
            "status": new_status,
            "updated_at": func.now()
        }

        return self._execute_update(
            query,
            update_values,
            f"Failed updating case status case_id={case_id}"
        )

    def resolve_case(self, case_id: str) -> bool:
        """
        Mark escalation resolved.
        """
        query = self.session.query(EscalationCase).filter(
            EscalationCase.case_id == case_id
        )
        
        update_values = {
            "status": "resolved",
            "resolved_at": func.now(),
            "updated_at": func.now()
        }

        return self._execute_update(
            query,
            update_values,
            f"Failed resolving case case_id={case_id}"
        )