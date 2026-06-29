from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from layer_2_proactive_agent.database.model.proactive_event_record import (
    ProactiveEventRecord,
)


class ProactiveEventRepository:
    """
    Repository for proactive workflow audit events.

    Handles:
    - persistence
    - history lookups
    - analytics retrieval

    NOTE:
    Transaction commit is managed by caller.
    """

    def __init__(
        self,
        session: Session,
    ):
        self.session = session

    def save_event(
        self,
        event: ProactiveEventRecord,
    ) -> ProactiveEventRecord:
        """
        Persist workflow audit event.
        """

        self.session.add(event)
        self.session.flush()

        return event

    def get_by_workflow(
        self,
        workflow_id: str,
    ) -> Optional[ProactiveEventRecord]:
        """
        Retrieve event by workflow id.
        """

        stmt = (
            select(ProactiveEventRecord)
            .where(
                ProactiveEventRecord.workflow_id
                == workflow_id
            )
        )

        return self.session.execute(
            stmt
        ).scalar_one_or_none()
    
    def get_recent_events(self, limit: int = 100) -> list[ProactiveEventRecord]:
        """
        Retrieve a global chronological list of all recent proactive events.
        Useful for admin dashboards and activity streams.
        """
        stmt = (
            select(ProactiveEventRecord)
            .order_by(ProactiveEventRecord.created_at.desc())
            .limit(limit)
        )
        return list(self.session.execute(stmt).scalars().all())

    def get_customer_history(
        self,
        customer_id: int,
    ) -> list[ProactiveEventRecord]:
        """
        Retrieve all proactive events
        for a customer.
        """

        stmt = (
            select(ProactiveEventRecord)
            .where(
                ProactiveEventRecord.customer_id
                == customer_id
            )
            .order_by(
                ProactiveEventRecord.created_at.desc()
            )
        )

        return list(
            self.session.execute(stmt)
            .scalars()
            .all()
        )

    def get_signal_history(
        self,
        signal_type: str,
    ) -> list[ProactiveEventRecord]:
        """
        Retrieve all events
        for a signal type.
        """

        stmt = (
            select(ProactiveEventRecord)
            .where(
                ProactiveEventRecord.signal_type
                == signal_type
            )
            .order_by(
                ProactiveEventRecord.created_at.desc()
            )
        )

        return list(
            self.session.execute(stmt)
            .scalars()
            .all()
        )