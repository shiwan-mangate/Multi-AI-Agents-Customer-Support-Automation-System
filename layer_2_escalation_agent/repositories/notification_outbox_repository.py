import logging
from typing import Dict, Any, List

from sqlalchemy.orm import Session
from sqlalchemy import func

from layer_2_escalation_agent.schemas.notification_job import NotificationJob

# Importing the exact model we just built
from layer_2_escalation_agent.db.model.notification_outbox_model import NotificationOutbox

logger = logging.getLogger(__name__)

class NotificationOutboxRepository:
    """
    Repository for notification outbox lifecycle management.

    Responsibilities:
    - queue notification jobs
    - fetch pending jobs
    - mark delivery lifecycle states

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
            
            # Flush to database immediately to catch errors without committing
            self.session.flush()
            return True

        except Exception as exc:
            logger.error("%s | Error: %s", error_message, str(exc))
            raise

    def _base_query(self):
        """Helper to ensure consistent SELECT * dictionary returns."""
        return self.session.query(*NotificationOutbox.__table__.columns)

    def enqueue_job(self, job: NotificationJob) -> bool:
        """
        Queue NotificationJob object.
        """
        payload = (
            job.payload
            if isinstance(job.payload, dict)
            else {}
        )

        channel_val = (
            job.channel.value
            if hasattr(job.channel, "value")
            else str(job.channel)
        )

        try:
            new_notification = NotificationOutbox(
                case_id=job.case_id,
                channel=channel_val,
                recipient=job.recipient,
                payload=payload,  # Natively handled by JSONB
                status='pending',
                retry_count=0,
                last_error=None,
                processed_at=None
            )

            self.session.add(new_notification)
            self.session.flush()
            return True

        except Exception as exc:
            logger.error("Failed enqueuing notification case_id=%s | Error: %s", job.case_id, str(exc))
            raise

    def enqueue_notification(
        self,
        case_id: str,
        channel: str,
        recipient: str,
        payload: Dict[str, Any],
    ) -> bool:
        """
        Backward-compatible helper.
        """
        try:
            new_notification = NotificationOutbox(
                case_id=case_id,
                channel=channel,
                recipient=recipient,
                payload=payload,
                status='pending',
                retry_count=0,
                last_error=None,
                processed_at=None
            )

            self.session.add(new_notification)
            self.session.flush()
            return True

        except Exception as exc:
            logger.error("Failed enqueuing notification case_id=%s | Error: %s", case_id, str(exc))
            raise

    # =========================================================
    # FETCH (Read-Only)
    # =========================================================

    def fetch_pending_notifications(
        self,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        
        try:
            results = self._base_query().filter(
                NotificationOutbox.status == 'pending'
            ).order_by(
                NotificationOutbox.created_at.asc()
            ).limit(limit).all()

            return [row._asdict() for row in results]

        except Exception:
            logger.exception("Failed fetching pending notifications")
            return []

    def get_case_notifications(
        self,
        case_id: str
    ) -> List[Dict[str, Any]]:
        
        try:
            results = self._base_query().filter(
                NotificationOutbox.case_id == case_id
            ).order_by(
                NotificationOutbox.created_at.desc()
            ).all()

            return [row._asdict() for row in results]

        except Exception:
            logger.exception(
                "Failed fetching notifications case_id=%s",
                case_id
            )
            return []

    # =========================================================
    # STATUS UPDATES (Mutations)
    # =========================================================

    def mark_processing(
        self,
        notification_id: int
    ) -> bool:
        
        query = self.session.query(NotificationOutbox).filter(
            NotificationOutbox.id == notification_id,
            NotificationOutbox.status == 'pending'
        )

        return self._execute_update(
            query,
            {"status": "processing"},
            f"Failed claiming notification id={notification_id}"
        )

    def mark_sent(
        self,
        notification_id: int
    ) -> bool:
        
        query = self.session.query(NotificationOutbox).filter(
            NotificationOutbox.id == notification_id
        )

        update_values = {
            "status": "sent",
            "processed_at": func.now(),
            "last_error": None
        }

        return self._execute_update(
            query,
            update_values,
            f"Failed marking sent notification id={notification_id}"
        )

    def mark_failed(
        self,
        notification_id: int,
        error_message: str
    ) -> bool:
        
        query = self.session.query(NotificationOutbox).filter(
            NotificationOutbox.id == notification_id
        )

        update_values = {
            "status": "failed",
            # Atomic incrementation natively supported by SQLAlchemy
            "retry_count": NotificationOutbox.retry_count + 1,
            "last_error": error_message,
            "processed_at": func.now()
        }

        return self._execute_update(
            query,
            update_values,
            f"Failed marking failed notification id={notification_id}"
        )