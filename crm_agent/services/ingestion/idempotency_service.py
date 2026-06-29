# crm_agent/services/ingestion/idempotency_service.py

import logging

from crm_agent.repositories.processed_event_repository import (
    ProcessedEventRepository,
)
from crm_agent.schemas.crm_event import CRMResolvedEvent
from crm_agent.db.models.processed_event_model import ProcessedEvent


logger = logging.getLogger(__name__)


class IdempotencyService:
    """
    Orchestration layer managing event deduplication and terminal state records.
    """

    def __init__(
        self,
        processed_repo: ProcessedEventRepository
    ):
        self.processed_repo = processed_repo

    def is_duplicate_event(
        self,
        event: CRMResolvedEvent
    ) -> bool:

        event_id = event.event.event_id

        is_processed = self.processed_repo.is_processed(event_id)

        if is_processed:
            logger.info(
                "Duplicate event detected | event_id=%s",
                event_id
            )
            return True

        logger.info(
            "Unique event detected | event_id=%s",
            event_id
        )

        return False

    def mark_success(
        self,
        event: CRMResolvedEvent
    ) -> ProcessedEvent:

        event_id = event.event.event_id

        record = self.processed_repo.mark_processed(event_id)

        logger.info(
            "Event marked SUCCESS | event_id=%s",
            event_id
        )

        return record

    def mark_dead(
        self,
        event: CRMResolvedEvent
    ) -> ProcessedEvent:

        event_id = event.event.event_id

        record = self.processed_repo.mark_dead(event_id)

        logger.error(
            "Event marked DEAD | event_id=%s",
            event_id
        )

        return record