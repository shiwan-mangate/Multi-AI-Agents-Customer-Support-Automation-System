# crm_agent/services/ingestion/event_consumer.py

import logging
import signal
import socket
import time
import uuid
from datetime import datetime, UTC, timedelta
from typing import Callable, List

from pydantic import ValidationError
from sqlalchemy import update
from sqlalchemy.orm import Session, sessionmaker

from crm_agent.db.models.crm_event_model import CRMEvent
from crm_agent.schemas.crm_event import CRMResolvedEvent
from crm_agent.services.ingestion.event_claim_service import (
    EventClaimService,
)
from crm_agent.services.processing.event_processor import (
    EventProcessor,
)

logger = logging.getLogger(__name__)


class CRMEventConsumer:
    """
    Distributed PostgreSQL-backed worker daemon.
    """

    def __init__(
        self,
        session_factory: sessionmaker,
        processor_factory: Callable[[Session], EventProcessor],
        claim_service_factory: Callable[[Session], EventClaimService],
        batch_size: int = 5,
        idle_sleep_seconds: float = 2.0,
        stale_recovery_minutes: int = 15,
    ):
        self.session_factory = session_factory

        self.processor_factory = processor_factory
        self.claim_service_factory = claim_service_factory

        self.batch_size = batch_size
        self.idle_sleep_seconds = idle_sleep_seconds
        self.stale_recovery_minutes = stale_recovery_minutes

        hostname = socket.gethostname()

        self.worker_id = (
            f"crm-worker-"
            f"{hostname}-"
            f"{uuid.uuid4().hex[:8]}"
        )

        self.is_running = False

        self._last_stale_recovery = (
            datetime.now(UTC) - timedelta(days=1)
        )

        signal.signal(
            signal.SIGINT,
            self._handle_shutdown,
        )

        signal.signal(
            signal.SIGTERM,
            self._handle_shutdown,
        )

    def _handle_shutdown(
        self,
        signum,
        frame
    ) -> None:
        logger.warning(
            "Shutdown signal received | worker=%s",
            self.worker_id,
        )
        self.is_running = False

    def start(self) -> None:
        self.is_running = True

        logger.info(
            "CRM worker started | worker=%s",
            self.worker_id,
        )

        while self.is_running:
            self._run_maintenance_if_needed()

            events = self._claim_batch()

            if not events:
                time.sleep(
                    self.idle_sleep_seconds
                )
                continue

            for db_event in events:
                if not self.is_running:
                    logger.warning(
                        "Worker stopping mid-batch | worker=%s",
                        self.worker_id,
                    )
                    break

                self._process_single_event(
                    db_event
                )

        logger.info(
            "Worker stopped | worker=%s",
            self.worker_id,
        )

    def _claim_batch(self) -> List[CRMEvent]:
        with self.session_factory() as session:
            claim_service = (
                self.claim_service_factory(
                    session
                )
            )

            try:
                events = claim_service.claim_events(
                    worker_id=self.worker_id,
                    batch_size=self.batch_size,
                )

                try:
                    session.commit()
                except Exception:
                    session.rollback()
                    raise

                for event in events:
                    session.expunge(event)

                return events

            except Exception as e:
                session.rollback()

                logger.exception(
                    "Batch claim failed | worker=%s | error=%s",
                    self.worker_id,
                    str(e),
                )

                time.sleep(
                    self.idle_sleep_seconds * 2
                )

                return []

    def _process_single_event(
        self,
        db_event: CRMEvent
    ) -> None:
        with self.session_factory() as session:
            processor = self.processor_factory(
                session
            )

            try:
                resolved_event = (
                    CRMResolvedEvent.model_validate(
                        db_event.payload
                    )
                )

                processor.process_event(
                    resolved_event
                )

            except ValidationError as ve:
                logger.error(
                    "Schema validation failed | event_id=%s | error=%s",
                    db_event.event_id,
                    str(ve),
                )

                session.rollback()

                self._mark_poison_pill_dead(
                    session=session,
                    event_id=db_event.event_id,
                    error_msg=str(ve),
                )

            except Exception as e:
                session.rollback()

                logger.exception(
                    "Unhandled worker failure | event_id=%s | error=%s",
                    db_event.event_id,
                    str(e),
                )

    def _mark_poison_pill_dead(
        self,
        session: Session,
        event_id: str,
        error_msg: str,
    ) -> None:
        try:
            now = datetime.now(UTC)
            stmt = (
                update(CRMEvent)
                .where(CRMEvent.event_id == event_id)
                .values(
                    status="DEAD",
                    last_error=(
                        "Pydantic Validation Error: "
                        f"{error_msg}"
                    ),
                    processed_at=now,
                    updated_at=now,  # Synchronized tracking metadata column maps securely
                    claimed_by=None,
                    claimed_at=None,
                )
            )

            session.execute(stmt)
            try:
                session.commit()
            except Exception:
                session.rollback()
                raise
        except Exception :
            session.rollback()

    def _run_maintenance_if_needed(
        self
    ) -> None:
        now = datetime.now(UTC)

        should_run = (
            now - self._last_stale_recovery
        ) > timedelta(
            minutes=self.stale_recovery_minutes
        )

        if not should_run:
            return

        with self.session_factory() as session:
            claim_service = (
                self.claim_service_factory(
                    session
                )
            )

            try:
                claim_service.release_stale_claims(
                    timeout_minutes=self.stale_recovery_minutes
                )
            except Exception as e:
                logger.exception(
                    "Stale recovery failed | worker=%s | error=%s",
                    self.worker_id,
                    str(e),
                )

        self._last_stale_recovery = now