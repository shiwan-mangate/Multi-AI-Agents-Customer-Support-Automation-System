from datetime import datetime, UTC
from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from crm_agent.db.models.processed_event_model import ProcessedEvent


class ProcessedEventRepository:
    """
    CRM idempotency repository.
    Prevents duplicate event processing.
    """

    def __init__(self, session: Session):
        self.session = session

    def is_processed(self, event_id: str) -> bool:
        stmt = select(ProcessedEvent).where(
            ProcessedEvent.event_id == event_id
        )

        record = self.session.execute(stmt).scalar_one_or_none()
        return record is not None

    def mark_processed(self, event_id: str) -> ProcessedEvent:
        return self._mark_terminal(event_id, "SUCCESS")

    def mark_dead(self, event_id: str) -> ProcessedEvent:
        return self._mark_terminal(event_id, "DEAD")

    def _mark_terminal(
        self,
        event_id: str,
        result_status: str
    ) -> ProcessedEvent:
        record = ProcessedEvent(
            event_id=event_id,
            processed_at=datetime.now(UTC),
            result_status=result_status,
        )

        self.session.add(record)
        return record

    def get_by_event_id(
        self,
        event_id: str
    ) -> Optional[ProcessedEvent]:
        stmt = select(ProcessedEvent).where(
            ProcessedEvent.event_id == event_id
        )

        return self.session.execute(stmt).scalar_one_or_none()