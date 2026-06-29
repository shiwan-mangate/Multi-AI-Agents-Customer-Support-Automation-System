from datetime import datetime, timedelta, UTC
from typing import List, Optional

from sqlalchemy import select, update, delete
from sqlalchemy.orm import Session

from crm_agent.db.models.crm_event_model import CRMEvent
from crm_agent.schemas.crm_event import CRMResolvedEvent


class CRMEventRepository:
    """
    PostgreSQL distributed CRM queue repository.
    """

    def __init__(self, session: Session):
        self.session = session

    def create_event(self, event_data: CRMResolvedEvent) -> CRMEvent:
        db_event = CRMEvent(
            event_id=event_data.event.event_id,
            event_type=event_data.event.event_type,
            source_agent=event_data.event.source_agent,
            schema_version=event_data.event.schema_version,
            payload=event_data.model_dump(mode="json"),
            status="NEW",
            retry_count=0,
        )

        self.session.add(db_event)
        return db_event

    def claim_events_for_processing(
        self,
        worker_id: str,
        batch_size: int = 5
    ) -> List[CRMEvent]:
        stmt = (
            select(CRMEvent)
            .where(CRMEvent.status == "NEW")
            .order_by(CRMEvent.created_at.asc())
            .limit(batch_size)
            .with_for_update(skip_locked=True)
        )

        events = self.session.scalars(stmt).all()

        if not events:
            return []

        now = datetime.now(UTC)

        for event in events:
            event.status = "PROCESSING"
            event.claimed_by = worker_id
            event.claimed_at = now

        self.session.flush()
        return events

    def mark_done(self, event_id: str) -> None:
        stmt = (
            update(CRMEvent)
            .where(CRMEvent.event_id == event_id)
            .values(
                status="DONE",
                processed_at=datetime.now(UTC),
                claimed_by=None,
                claimed_at=None,
            )
        )

        self.session.execute(stmt)
        self.session.flush()

    def mark_failed(
        self,
        event_id: str,
        error_msg: str,
        max_retries: int = 3
    ) -> None:
        event = self.get_by_event_id(event_id)

        if not event:
            return

        retry_count = event.retry_count + 1

        if retry_count >= max_retries:
            self.mark_dead(event_id, error_msg)
            return

        stmt = (
            update(CRMEvent)
            .where(CRMEvent.event_id == event_id)
            .values(
                status="FAILED",
                retry_count=retry_count,
                last_error=error_msg,
                claimed_by=None,
                claimed_at=None,
            )
        )

        self.session.execute(stmt)
        self.session.flush()

    def mark_dead(self, event_id: str, final_error: str) -> None:
        stmt = (
            update(CRMEvent)
            .where(CRMEvent.event_id == event_id)
            .values(
                status="DEAD",
                last_error=final_error,
                processed_at=datetime.now(UTC),
                claimed_by=None,
                claimed_at=None,
            )
        )

        self.session.execute(stmt)
        self.session.flush()

    def get_by_event_id(self, event_id: str) -> Optional[CRMEvent]:
        stmt = select(CRMEvent).where(CRMEvent.event_id == event_id)
        return self.session.execute(stmt).scalar_one_or_none()


    def replay_failed_events(
        self,
        limit: int = 100,
    ) -> int:
        """
        Requeue FAILED events back to NEW status.
        Clears:
        - worker ownership
        - claim timestamp
        - error metadata
        Returns:
            Number of events replayed.
        """
        subquery = (
            self.session.query(
                CRMEvent.event_id
            )
            .filter(
                CRMEvent.status == "FAILED"
            )
            .order_by(
                CRMEvent.created_at.asc()
            )
            .limit(limit)
            .subquery()
        )
        stmt = (
            update(CRMEvent)
            .where(
                CRMEvent.event_id.in_(
                    select(subquery.c.event_id)
                )
            )
            .values(
                status="NEW",
                claimed_by=None,
                claimed_at=None,
                last_error=None,
            )
            .execution_options(
                synchronize_session=False
            )
        )
        result = self.session.execute(stmt)
        self.session.flush()
        return result.rowcount or 0
    

    def cleanup_dead_events(
            self,
            retention_days: int = 90,
        ) -> int:
            """
            Permanently removes DEAD events older than
            the retention window.
            """

            cutoff_date = (
                datetime.now(UTC)
                - timedelta(days=retention_days)
            )

            stmt = (
                delete(CRMEvent)
                .where(CRMEvent.status == "DEAD")
                # Adjusted column pointer to use processed_at to align with the schema log
                .where(
                    CRMEvent.processed_at <= cutoff_date
                )
                .execution_options(
                    synchronize_session=False
                )
            )

            result = self.session.execute(stmt)
            self.session.flush()

            return result.rowcount or 0