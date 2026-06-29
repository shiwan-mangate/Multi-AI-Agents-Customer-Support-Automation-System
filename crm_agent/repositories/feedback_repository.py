from datetime import datetime, UTC, timedelta
from typing import List, Optional

from sqlalchemy import select, update, desc, or_
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from crm_agent.db.models.feedback_model import FeedbackSignal


class FeedbackRepository:
    """
    Feedback intelligence repository.
    """

    def __init__(self, session: Session):
        self.session = session

    def create_feedback(
        self,
        ticket_id: str,
        customer_id: int,  # Maps directly to the schema's bigint column type
        source_agent: str,
        feedback_type: str,
        rating: int,
        comment: Optional[str] = None,
        feedback_channel: Optional[str] = None,
        resolution_type: Optional[str] = None,
        status: Optional[str] = None,
    ) -> Optional[FeedbackSignal]:

        if self.get_by_ticket_id(ticket_id):
            return None

        feedback = FeedbackSignal(
            ticket_id=ticket_id,
            customer_id=customer_id,
            source_agent=source_agent,
            feedback_type=feedback_type,
            rating=rating,
            comment=comment,
            feedback_channel=feedback_channel,
            resolution_type=resolution_type,
            status=status,
            processed_for_churn=False,
        )

        try:
            self.session.add(feedback)
            self.session.flush()
            return feedback
        except IntegrityError:
            self.session.rollback()
            return None

    def get_by_ticket_id(
        self,
        ticket_id: str
    ) -> Optional[FeedbackSignal]:
        stmt = select(FeedbackSignal).where(
            FeedbackSignal.ticket_id == ticket_id
        )

        return self.session.execute(stmt).scalar_one_or_none()

    def get_unprocessed_negative_feedback(
        self,
        batch_size: int = 50
    ) -> List[FeedbackSignal]:

        stmt = (
            select(FeedbackSignal)
            .where(FeedbackSignal.processed_for_churn.is_(False))
            .where(
                or_(
                    FeedbackSignal.rating < 0,
                    FeedbackSignal.rating.in_([1, 2])
                )
            )
            .order_by(FeedbackSignal.created_at.asc())
            .limit(batch_size)
            .with_for_update(skip_locked=True)
        )

        return list(self.session.scalars(stmt).all())

    def mark_processed_for_churn(self, feedback_id: str) -> None:
        stmt = (
            update(FeedbackSignal)
            .where(FeedbackSignal.feedback_id == feedback_id)
            .values(
                processed_for_churn=True
            )
        )

        self.session.execute(stmt)

    def get_agent_feedback(
        self,
        source_agent: str,
        days: int = 30
    ) -> List[FeedbackSignal]:

        cutoff = datetime.now(UTC) - timedelta(days=days)

        stmt = (
            select(FeedbackSignal)
            .where(FeedbackSignal.source_agent == source_agent)
            .where(FeedbackSignal.created_at >= cutoff)
            .order_by(desc(FeedbackSignal.created_at))
        )

        return list(self.session.scalars(stmt).all())