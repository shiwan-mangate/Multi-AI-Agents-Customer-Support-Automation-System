from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
import logging

from layer_2_account_agent.schemas.domain import ActionType

# Importing the exact models we generated for the Account Agent
from layer_2_account_agent.db.model.account_security_audit_model import AccountSecurityAudit
from layer_2_account_agent.db.model.idempotency_keys_model import IdempotencyKey

logger = logging.getLogger(__name__)

VALID_IDEMPOTENCY_STATUS = {"processing", "completed", "failed"}

class SecurityAuditRepository:
    """
    Repository for:
    1. Immutable security audit logging
    2. Idempotency execution control
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
        Executes ORM UPDATE mutations safely with transaction handling.
        """
        try:
            # SQLAlchemy native update command
            rowcount = query.update(update_values, synchronize_session=False)

            if rowcount == 0:
                self.session.rollback()
                logger.warning("%s | No rows affected.", error_message)
                return False

            try:
                self.session.commit()
            except Exception:
                self.session.rollback()
                raise
                
            return True

        except Exception:
            self.session.rollback()
            logger.exception(error_message)
            return False

    def log_security_event(
        self,
        workflow_id: str,
        correlation_id: str,
        action_type: str,
        decision: str,
        customer_id: Optional[int] = None,
        ticket_id: Optional[str] = None,
        verification_level: Optional[str] = None,
        risk_score: float = 0.0,
        provider_response: Optional[Dict[str, Any]] = None,
        operator_type: str = "AI"
    ) -> bool:
        """
        Immutable audit logging with forced parent-record resolution.
        """
        try:
            # Standard ORM instantiation for INSERT
            audit_record = AccountSecurityAudit(
                ticket_id=ticket_id,
                customer_id=customer_id,
                workflow_id=workflow_id,
                correlation_id=correlation_id,
                action_type=action_type,
                verification_level=verification_level,
                risk_score=risk_score,
                decision=decision,
                # JSONB automatically handles the Python dict natively, no json.dumps required
                provider_response=provider_response,
                operator_type=operator_type
            )

            self.session.add(audit_record)
            
            try:
                self.session.commit()
            except Exception:
                self.session.rollback()
                raise
                
            return True

        except Exception:
            self.session.rollback()
            logger.exception("Failed logging audit event workflow_id=%s", workflow_id)
            return False

    def create_idempotency_record(
        self,
        idempotency_key: str,
        action_type: ActionType,
        customer_id: Optional[int]
    ) -> bool:
        try:
            new_record = IdempotencyKey(
                idempotency_key=idempotency_key,
                action_type=action_type.value,
                customer_id=customer_id,
                status='processing'
            )

            self.session.add(new_record)
            
            try:
                self.session.commit()
            except Exception:
                self.session.rollback()
                raise
                
            return True

        except IntegrityError:
            # Expected behavior when the idempotency key already exists (Concurrency Guard)
            self.session.rollback()
            return False

        except Exception:
            self.session.rollback()
            logger.exception(
                "Failed creating idempotency record key=%s",
                idempotency_key
            )
            return False

    def update_idempotency_status(
        self,
        idempotency_key: str,
        status: str,
        response_payload: Optional[Dict[str, Any]] = None
    ) -> bool:

        if status not in VALID_IDEMPOTENCY_STATUS:
            logger.warning("Invalid idempotency status: %s", status)
            return False

        query = self.session.query(IdempotencyKey).filter(
            IdempotencyKey.idempotency_key == idempotency_key
        )

        update_values = {
            "status": status,
            # JSONB automatically serializes the dictionary natively
            "response_payload": response_payload
        }

        return self._execute_update(
            query,
            update_values,
            f"Failed updating idempotency key={idempotency_key}"
        )

    def get_idempotency_record(
        self,
        idempotency_key: str
    ) -> Optional[Dict[str, Any]]:
        try:
            result = self.session.query(
                IdempotencyKey.idempotency_key,
                IdempotencyKey.action_type,
                IdempotencyKey.customer_id,
                IdempotencyKey.status,
                IdempotencyKey.response_payload,
                IdempotencyKey.created_at
            ).filter(
                IdempotencyKey.idempotency_key == idempotency_key
            ).first()

            return result._asdict() if result else None

        except Exception:
            logger.exception(
                "Failed fetching idempotency record key=%s",
                idempotency_key
            )
            return None