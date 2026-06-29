from datetime import datetime, UTC, timedelta
from typing import List, Optional
import logging

from sqlalchemy import select, desc, or_
from sqlalchemy.orm import Session

from crm_agent.db.models.transcript_model import TranscriptRecord
from crm_agent.schemas.crm_event import CRMResolvedEvent

logger = logging.getLogger(__name__)

class TranscriptRepository:
    """
    Immutable transcript ledger repository.
    """

    def __init__(self, session: Session):
        self.session = session

    def create_transcript(
        self,
        event: CRMResolvedEvent
    ) -> TranscriptRecord:
        try:
            # 1. Safely serialize Pydantic objects for PostgreSQL JSONB
            # If we don't do this, Postgres will reject the array and silently roll back.
            messages_data = []
            if event.conversation and event.conversation.messages:
                messages_data = [
                    msg.model_dump() if hasattr(msg, 'model_dump') else msg 
                    for msg in event.conversation.messages
                ]

            agents_data = []
            if event.conversation and event.conversation.agents_involved:
                agents_data = [
                    agent.model_dump() if hasattr(agent, 'model_dump') else agent 
                    for agent in event.conversation.agents_involved
                ]

            transcript = TranscriptRecord(
                ticket_id=event.ticket.ticket_id,
                customer_id=event.customer.customer_id, 
                source_agent=event.event.source_agent,
                workflow_id=event.ticket.workflow_id,
                trace_id=event.ticket.trace_id,
                channel=event.ticket.channel,

                # Injected the safely serialized lists
                messages=messages_data,
                agents_involved=agents_data,
                original_message=event.conversation.original_message if event.conversation else None,
                translated_message=event.conversation.translated_message if event.conversation else None,

                intent=event.analytics.intent if event.analytics else None,
                priority=event.analytics.priority if event.analytics else None,
                sentiment_start=event.analytics.sentiment_start if event.analytics else None,
                sentiment_end=event.analytics.sentiment_end if event.analytics else None,
                issue_tags=event.analytics.issue_tags if event.analytics else [],

                status=event.resolution.status,
                resolution_type=event.resolution.resolution_type,
                resolution_message=event.resolution.resolution_message,
                resolved_by=event.resolution.resolved_by,
                time_to_resolution_ms=event.resolution.time_to_resolution_ms,

                created_at=datetime.now(UTC),
            )
            logger.warning(
                "DB INTENT = %s",
                event.analytics.intent if event.analytics else None
            )

            self.session.add(transcript)
            
            # 2. CRITICAL FIX: Explicit commit to save the async CRM event to the database
            self.session.flush()
            
            return transcript
            
        except Exception as e:
            self.session.rollback()
            logger.error(f"❌ Failed to persist transcript for ticket {event.ticket.ticket_id}: {e}")
            raise

    def get_by_ticket_id(
        self,
        ticket_id: str
    ) -> Optional[TranscriptRecord]:
        stmt = select(TranscriptRecord).where(
            TranscriptRecord.ticket_id == ticket_id
        )
        return self.session.execute(stmt).scalar_one_or_none()

    def get_customer_history(
        self,
        customer_id: int,
        limit: int = 10
    ) -> List[TranscriptRecord]:
        stmt = (
            select(TranscriptRecord)
            .where(TranscriptRecord.customer_id == customer_id)
            .order_by(desc(TranscriptRecord.created_at))
            .limit(limit)
        )
        return list(self.session.scalars(stmt).all())

    def get_recent_negative_transcripts(
        self,
        customer_id: int,
        days: int = 30
    ) -> List[TranscriptRecord]:
        cutoff = datetime.now(UTC) - timedelta(days=days)
        stmt = (
            select(TranscriptRecord)
            .where(TranscriptRecord.customer_id == customer_id)
            .where(TranscriptRecord.created_at >= cutoff)
            .where(
                or_(
                    TranscriptRecord.sentiment_end.in_(["frustrated", "angry"]),
                    TranscriptRecord.status.in_(["failed", "denied", "escalated"]),
                )
            )
            .order_by(desc(TranscriptRecord.created_at))
        )
        return list(self.session.scalars(stmt).all())
    
    def update_transcript(self,transcript: TranscriptRecord,event: CRMResolvedEvent) -> TranscriptRecord:
        """
        Updates an existing transcript after a paused workflow resumes
        (e.g. Escalation, Refund Approval, Account Review).

        The transcript represents the latest state of the ticket while
        preserving the original record identity.
        """
        try:
            # ---------------------------------------------
            # Serialize JSON payloads safely for PostgreSQL
            # ---------------------------------------------
            messages_data = []
            if event.conversation and event.conversation.messages:
                messages_data = [
                    msg.model_dump() if hasattr(msg, "model_dump") else msg
                    for msg in event.conversation.messages
                ]

            agents_data = []
            if event.conversation and event.conversation.agents_involved:
                agents_data = [
                    agent.model_dump() if hasattr(agent, "model_dump") else agent
                    for agent in event.conversation.agents_involved
                ]

            # ---------------------------------------------
            # Conversation
            # ---------------------------------------------
            transcript.messages = messages_data
            transcript.agents_involved = agents_data
            transcript.original_message = (
                event.conversation.original_message
                if event.conversation else None
            )
            transcript.translated_message = (
                event.conversation.translated_message
                if event.conversation else None
            )

            # ---------------------------------------------
            # Analytics
            # ---------------------------------------------
            if event.analytics:
                transcript.intent = event.analytics.intent
                transcript.priority = event.analytics.priority
                transcript.sentiment_start = event.analytics.sentiment_start
                transcript.sentiment_end = event.analytics.sentiment_end
                transcript.issue_tags = event.analytics.issue_tags

            # ---------------------------------------------
            # Resolution (this is what changes after resume)
            # ---------------------------------------------
            transcript.status = event.resolution.status
            transcript.resolution_type = event.resolution.resolution_type
            transcript.resolution_message = event.resolution.resolution_message
            transcript.resolved_by = event.resolution.resolved_by
            transcript.time_to_resolution_ms = (
                event.resolution.time_to_resolution_ms
            )

            # ---------------------------------------------
            # Metadata
            # ---------------------------------------------
            transcript.source_agent = event.event.source_agent

            # If your model has updated_at, update it.
            if hasattr(transcript, "updated_at"):
                transcript.updated_at = datetime.now(UTC)

            self.session.flush()
            self.session.refresh(transcript)

            logger.info(
                "Transcript updated | ticket_id=%s",
                transcript.ticket_id
            )

            return transcript

        except Exception as e:
            self.session.rollback()
            logger.error(
                "❌ Failed to update transcript | ticket_id=%s | error=%s",
                transcript.ticket_id,
                e,
                exc_info=True,
            )
            raise