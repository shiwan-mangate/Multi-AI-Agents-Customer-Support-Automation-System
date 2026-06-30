# crm_agent/services/transcript/transcript_service.py

import logging
from typing import List, Optional

from crm_agent.schemas.crm_event import CRMResolvedEvent
# Inconsistency Fix: Pointed import statement to the correct model file name
from crm_agent.db.models.transcript_model import TranscriptRecord
from crm_agent.repositories.transcript_repository import (
    TranscriptRepository,
)

logger = logging.getLogger(__name__)


class TranscriptService:
    """
    Business orchestration layer for the immutable Audit Ledger.

    Responsibilities:
    - Validate event integrity.
    - Prevent duplicate transcript creation.
    - Delegate persistence to the repository.

    Does NOT:
    - Execute SQL directly.
    - Calculate churn.
    - Create alerts.
    """

    def __init__(
        self,
        transcript_repo: TranscriptRepository,
    ):
        self.transcript_repo = transcript_repo


    def create_transcript(
        self,
        event: CRMResolvedEvent,
    ) -> TranscriptRecord:

        ticket_id = event.ticket.ticket_id

        logger.warning(
        "TRANSCRIPT SERVICE CALLED | ticket=%s",
        ticket_id,
    )

        self._validate_event(event)

        existing = (
            self.transcript_repo.get_by_ticket_id(
                ticket_id
            )
        )

        if existing is not None:
            logger.info(
                "Transcript already exists | ticket_id=%s",
                ticket_id,
            )
            return self.transcript_repo.update_transcript(
        existing,
        event
    )

        record = self.transcript_repo.create_transcript(
            event
        )

        logger.info(
            "Transcript persisted | ticket_id=%s",
            ticket_id,
        )

        return record

    def _validate_event(
        self,
        event: CRMResolvedEvent,
    ) -> None:

        if not event.event.event_id:
            raise ValueError(
                "Cannot persist transcript: event_id is missing."
            )

        if not event.ticket.ticket_id:
            raise ValueError(
                "Cannot persist transcript: ticket_id is missing."
            )

        if event.customer.customer_id is None:
            raise ValueError(
                "Cannot persist transcript: customer_id is missing."
            )

        if not event.resolution.status:
            raise ValueError(
                "Cannot persist transcript: resolution status is missing."
            )

        if (
            hasattr(event, "conversation")
            and (
                not event.conversation
                or not event.conversation.messages
            )
        ):
            logger.warning(
                "Persisting transcript with empty conversation payload | ticket_id=%s",
                event.ticket.ticket_id,
            )


    def get_customer_history(
        self,
        customer_id: int,  # Maps cleanly to the refactored BigInteger DB identifier 
        limit: int = 10,
    ) -> List[TranscriptRecord]:

        logger.debug(
            "False-safe customer validation tracking | customer_id=%s | limit=%s",
            customer_id,
            limit,
        )

        return self.transcript_repo.get_customer_history(
            customer_id,
            limit,
        )

    def get_ticket_transcript(
        self,
        ticket_id: str,
    ) -> Optional[TranscriptRecord]:

        return self.transcript_repo.get_by_ticket_id(
            ticket_id
        )