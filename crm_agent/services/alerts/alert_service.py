import logging
from typing import Optional

from crm_agent.schemas.crm_event import CRMResolvedEvent
from crm_agent.schemas.churn import ChurnAssessment
from crm_agent.db.models.churn_alert_model import ChurnAlert
from crm_agent.repositories.churn_alert_repository import (
    ChurnAlertRepository,
)

logger = logging.getLogger(__name__)


class AlertService:
    """
    Business rule layer for operational risk alerts.

    Responsibilities:
    - Evaluate churn assessments.
    - Determine alert routing.
    - Enforce alert suppression.
    - Stage alerts in the Outbox.

    Does NOT:
    - Send Slack messages
    - Send emails
    - Execute webhooks
    """

    def __init__(
        self,
        alert_repo: ChurnAlertRepository,
    ):
        self.alert_repo = alert_repo


    def create_alert_if_needed(
        self,
        event: CRMResolvedEvent,
        assessment: ChurnAssessment,
    ) -> Optional[ChurnAlert]:

        customer_id = event.customer.customer_id

        if not self._is_alert_required(assessment):
            logger.debug(
                "No alert required | customer_id=%s | level=%s",
                customer_id,
                assessment.churn_level,
            )
            return None

        alert_type = self._determine_alert_type(
            event.customer.tier
        )

        if self._is_suppressed(
            customer_id=customer_id,
            alert_type=alert_type,
        ):
            logger.info(
                "Alert suppressed | customer_id=%s | type=%s",
                customer_id,
                alert_type,
            )
            return None

        # Securely pass exact types into the underlying repositories
        alert = self.alert_repo.create_alert(
            customer_id=customer_id,
            alert_type=alert_type,
            severity=assessment.churn_level,
            score=assessment.churn_score,
            reason=(
                f"{alert_type} threshold breached "
                f"at score {assessment.churn_score}"
            ),
            risk_reasons=assessment.risk_reasons,
            tier=event.customer.tier,
            ltv=event.customer.ltv,
            ticket_id=event.ticket.ticket_id,
            customer_email=event.customer.customer_email,
            source_agent=event.event.source_agent,
        )

        logger.warning(
            "Alert staged | customer_id=%s | type=%s | severity=%s",
            customer_id,
            alert_type,
            assessment.churn_level,
        )

        return alert


    def _is_alert_required(
    self,
    assessment: ChurnAssessment,
    ) -> bool:
        return assessment.churn_level in (
            "high",
            "urgent",
        )

    def _determine_alert_type(
    self,
    tier: Optional[str],
    ) -> str:
        tier = (tier or "").lower()
        if tier in {
            "enterprise",
            "premium",
        }:
            return "VIP_CHURN_RISK"
        return "CHURN_RISK"

    def _is_suppressed(
        self,
        customer_id: int,  # Strongly typed to prevent casting issues upstream
        alert_type: str,
    ) -> bool:

        existing_alert = (
            self.alert_repo.get_open_alert(
                customer_id=customer_id,
                alert_type=alert_type,
            )
        )

        return existing_alert is not None