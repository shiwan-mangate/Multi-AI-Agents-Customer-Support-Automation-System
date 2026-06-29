from datetime import datetime, UTC
from typing import List, Optional
from decimal import Decimal

from sqlalchemy import select, update
from sqlalchemy.orm import Session

from crm_agent.db.models.churn_alert_model import ChurnAlert


class ChurnAlertRepository:
    """
    Operational alert repository.
    """

    def __init__(self, session: Session):
        self.session = session

    def create_alert(
        self,
        customer_id: int,
        alert_type: str,
        severity: str,
        score: Decimal,
        reason: str,
        risk_reasons: List[str],
        tier: str = "standard",
        ltv: Decimal = Decimal("0.00"),
        ticket_id: Optional[str] = None,
        customer_email: Optional[str] = None,
        source_agent: Optional[str] = None,
    ) -> ChurnAlert:
        alert = ChurnAlert(
            customer_id=customer_id,
            ticket_id=ticket_id,
            customer_email=customer_email,
            tier=tier,
            ltv=ltv,
            source_agent=source_agent,
            alert_type=alert_type,
            severity=severity,
            score=score,
            reason=reason,
            risk_reasons=risk_reasons,
            alert_status="OPEN",
            delivery_status="PENDING",
        )

        self.session.add(alert)
        return alert

    def get_open_alert(
        self,
        customer_id: int,
        alert_type: str
    ) -> Optional[ChurnAlert]:
        stmt = (
            select(ChurnAlert)
            .where(ChurnAlert.customer_id == customer_id)
            .where(ChurnAlert.alert_type == alert_type)
            .where(ChurnAlert.alert_status.in_(["OPEN", "ACKNOWLEDGED"]))
        )

        return self.session.execute(stmt).scalar_one_or_none()

    def get_pending_delivery_alerts(
        self,
        batch_size: int = 10
    ) -> List[ChurnAlert]:
        stmt = (
            select(ChurnAlert)
            .where(ChurnAlert.delivery_status == "PENDING")
            .order_by(ChurnAlert.created_at.asc())
            .limit(batch_size)
            .with_for_update(skip_locked=True)
        )

        return list(self.session.scalars(stmt).all())

    def mark_delivery_sent(self, alert_id: str) -> None:
        stmt = (
            update(ChurnAlert)
            .where(ChurnAlert.alert_id == alert_id)
            .values(
                delivery_status="SENT",
                updated_at=datetime.now(UTC),
            )
        )

        self.session.execute(stmt)

    def mark_delivery_failed(self, alert_id: str) -> None:
        stmt = (
            update(ChurnAlert)
            .where(ChurnAlert.alert_id == alert_id)
            .values(
                delivery_status="FAILED",
                updated_at=datetime.now(UTC),
            )
        )

        self.session.execute(stmt)

    def acknowledge_alert(
        self,
        alert_id: str,
        operator_id: str
    ) -> None:
        stmt = (
            update(ChurnAlert)
            .where(ChurnAlert.alert_id == alert_id)
            .values(
                alert_status="ACKNOWLEDGED",
                acknowledged=True,
                acknowledged_by=operator_id,
                acknowledged_at=datetime.now(UTC),
                updated_at=datetime.now(UTC),
            )
        )

        self.session.execute(stmt)

    def resolve_alert(self, alert_id: str) -> None:
        stmt = (
            update(ChurnAlert)
            .where(ChurnAlert.alert_id == alert_id)
            .values(
                alert_status="RESOLVED",
                updated_at=datetime.now(UTC),
            )
        )

        self.session.execute(stmt)

    def get_by_alert_id(self, alert_id: str) -> Optional[ChurnAlert]:
        stmt = select(ChurnAlert).where(
            ChurnAlert.alert_id == alert_id
        )

        return self.session.execute(stmt).scalar_one_or_none()