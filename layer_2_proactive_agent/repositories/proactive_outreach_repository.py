from datetime import datetime, timedelta, UTC
from typing import Optional, List

from sqlalchemy import select, delete
from sqlalchemy.orm import Session

from layer_2_proactive_agent.database.model.proactive_outreach_record import (
    ProactiveOutreachRecord,
)

class ProactiveOutreachRepository:
    """
    Repository for proactive outreach registry.

    Handles:
    - suppression lookups
    - outreach persistence
    - suppression persistence
    - cleanup operations

    NOTE:
    Transaction commit is managed by the caller.
    """

    def __init__(self, session: Session):
        self.session = session

    def already_contacted(
        self,
        customer_id: int,
        signal_type: str,
    ) -> Optional[ProactiveOutreachRecord]:
        """
        Returns an active outreach record if suppression
        is still in effect.
        """
        stmt = (
            select(ProactiveOutreachRecord)
            .where(
                ProactiveOutreachRecord.customer_id == customer_id,
                ProactiveOutreachRecord.signal_type == signal_type,
                ProactiveOutreachRecord.expires_at > datetime.now(UTC),
            )
        )

        return self.session.execute(stmt).scalar_one_or_none()

    def record_outreach(
        self,
        record: ProactiveOutreachRecord,
    ) -> ProactiveOutreachRecord:
        """
        Persist a new outreach record.
        """
        self.session.add(record)
        self.session.flush()
        
        return record

    def record_suppression(
        self,
        record: ProactiveOutreachRecord,
    ) -> ProactiveOutreachRecord:
        """
        Persist a suppression record.
        (Functionally identical to record_outreach, kept for DDD naming clarity)
        """
        self.session.add(record)
        self.session.flush()
        
        return record

    def cleanup_expired_records(
        self,
        retention_days: int = 90,
    ) -> int:
        """
        Deletes expired suppression records.
        Keeps expired records for auditing up to `retention_days` after they expire.

        Returns:
            Number of deleted rows.
        """
        cutoff_date = datetime.now(UTC) - timedelta(days=retention_days)

        stmt = (
            delete(ProactiveOutreachRecord)
            .where(
                ProactiveOutreachRecord.expires_at < cutoff_date
            )
            .execution_options(synchronize_session=False)
        )

        result = self.session.execute(stmt)
        self.session.flush()

        return result.rowcount or 0

    def get_active_suppressions(
        self,
        customer_id: int,
    ) -> List[ProactiveOutreachRecord]:
        """
        Returns active suppression records for a customer.
        """
        stmt = (
            select(ProactiveOutreachRecord)
            .where(
                ProactiveOutreachRecord.customer_id == customer_id,
                ProactiveOutreachRecord.expires_at > datetime.now(UTC),
            )
        )

        return list(self.session.execute(stmt).scalars().all())