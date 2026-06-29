import logging
from datetime import datetime, UTC, timedelta
from typing import List

from sqlalchemy import update

from crm_agent.repositories.customer_event_repository import CRMEventRepository
from crm_agent.db.models.crm_event_model import CRMEvent

logger = logging.getLogger(__name__)

class EventClaimService:
    """
    Distributed queue ownership orchestration service.
    """

    def __init__(self, event_repo: CRMEventRepository):
        self.event_repo = event_repo

    def claim_events(
        self,
        worker_id: str,
        batch_size: int = 5
    ) -> List[CRMEvent]:

        logger.debug(
            "Worker [%s] attempting claim | batch_size=%d",
            worker_id,
            batch_size,
        )

        try:
            events = self.event_repo.claim_events_for_processing(
                worker_id=worker_id,
                batch_size=batch_size,
            )

            if events:
                logger.info(
                    "Worker [%s] claimed %d events",
                    worker_id,
                    len(events),
                )

            return events

        except Exception as e:
            logger.exception(
                "Worker [%s] failed claiming events | error=%s",
                worker_id,
                str(e),
            )
            raise

    def release_stale_claims(
        self,
        timeout_minutes: int = 15,
        max_retries: int = 3
    ) -> int:

        cutoff = datetime.now(UTC) - timedelta(minutes=timeout_minutes)
        now = datetime.now(UTC)

        logger.debug("Scanning stale claims | timeout_minutes=%d", timeout_minutes)

        try:
            # 1. Update stale 'PROCESSING' events to 'NEW'
            stmt = (
                update(CRMEvent)
                .where(CRMEvent.status == "PROCESSING")
                .where(CRMEvent.claimed_at.is_not(None))
                .where(CRMEvent.claimed_at < cutoff)
                .values(
                    status="NEW",
                    claimed_by=None,
                    claimed_at=None,
                    retry_count=CRMEvent.retry_count + 1,
                    updated_at=now,
                )
            )
            result = self.event_repo.session.execute(stmt)

            # 2. Mark retried-out events as 'DEAD'
            dead_stmt = (
                update(CRMEvent)
                .where(CRMEvent.retry_count >= max_retries)
                .where(CRMEvent.status == "NEW")
                .values(
                    status="DEAD",
                    processed_at=now,
                    updated_at=now,
                    last_error="Exceeded stale recovery retry limit.",
                )
            )
            self.event_repo.session.execute(dead_stmt)
            
            # 3. Finalize transaction: commit changes
            try:
                self.event_repo.session.commit()
            except Exception:
                self.event_repo.session.rollback()
                raise

            released_count = result.rowcount or 0
            if released_count > 0:
                logger.warning("Recovered %d stale events", released_count)

            return released_count

        except Exception as e:
            # 4. Rollback transaction on any failure
            self.event_repo.session.rollback()
            logger.exception("Failed stale claim recovery | error=%s", str(e))
            raise