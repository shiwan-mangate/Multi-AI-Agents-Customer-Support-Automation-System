import logging
from typing import Dict, Any, Optional, List

from sqlalchemy.orm import Session

from layer_2_escalation_agent.schemas.audit_record import AuditEventType, OperatorType

# Importing the exact EscalationAudit model we just verified
from layer_2_escalation_agent.db.model.escalation_audit_model import EscalationAudit

logger = logging.getLogger(__name__)

class AuditRepository:
    """
    Repository for immutable escalation audit event persistence.
    """

    def __init__(self, session: Session):
        self.session = session

    def _base_query(self):
        """
        Helper method to mirror 'SELECT *' and return consistent Row objects.
        """
        return self.session.query(
            EscalationAudit.audit_id,
            EscalationAudit.case_id,
            EscalationAudit.ticket_id,
            EscalationAudit.event_type,
            EscalationAudit.payload,
            EscalationAudit.operator_type,
            EscalationAudit.created_at
        )

    def log_event(
        self,
        case_id: str,
        ticket_id: Optional[str],
        event_type: AuditEventType,
        payload: Dict[str, Any],
        operator_type: OperatorType = OperatorType.AI,
    ) -> bool:
        """
        Persist audit event.

        Audit failure should NOT break workflow execution. Uses a nested 
        savepoint transaction to prevent repository failures from breaking 
        outer database context pools.
        """
        
        # 1. Start the nested transaction (savepoint)
        self.session.begin_nested()
        
        try:
            # Standard ORM instantiation. JSONB naturally handles the dict payload.
            audit_record = EscalationAudit(
                case_id=case_id,
                ticket_id=ticket_id,
                event_type=event_type.value if hasattr(event_type, "value") else str(event_type),
                payload=payload,
                operator_type=operator_type.value if hasattr(operator_type, "value") else str(operator_type)
            )

            self.session.add(audit_record)
            
            # 2. Commit the savepoint. If this succeeds, it merges into the outer transaction.
            self.session.commit()
            return True

        except Exception:
            # 3. CRITICAL FIX: Roll back the savepoint to prevent poisoning the outer Postgres transaction
            self.session.rollback()
            
            logger.exception(
                "Failed logging audit event case_id=%s event=%s. Continuing workflow execution.",
                case_id,
                event_type.value if hasattr(event_type, "value") else str(event_type)
            )
            return False

    def get_case_audit(
        self,
        case_id: str
    ) -> List[Dict[str, Any]]:
        """
        Fetch full audit trail for escalation case.
        """
        try:
            results = self._base_query().filter(
                EscalationAudit.case_id == case_id
            ).order_by(
                EscalationAudit.created_at.desc()
            ).all()

            return [row._asdict() for row in results]

        except Exception:
            logger.exception(
                "Failed fetching case audit case_id=%s",
                case_id
            )
            return []

    def get_ticket_audit(
        self,
        ticket_id: str
    ) -> List[Dict[str, Any]]:
        """
        Fetch audit events for ticket.
        """
        try:
            results = self._base_query().filter(
                EscalationAudit.ticket_id == ticket_id
            ).order_by(
                EscalationAudit.created_at.desc()
            ).all()

            return [row._asdict() for row in results]

        except Exception:
            logger.exception(
                "Failed fetching ticket audit ticket_id=%s",
                ticket_id
            )
            return []