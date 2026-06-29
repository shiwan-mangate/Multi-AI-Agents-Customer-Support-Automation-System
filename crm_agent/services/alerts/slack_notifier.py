import logging

from crm_agent.db.models.churn_alert_model import (
    ChurnAlert,
)

from crm_agent.repositories.churn_alert_repository import (
    ChurnAlertRepository,
)

logger = logging.getLogger(__name__)


class SlackNotifier:
    """
    Generic Notification Adapter.

    Phase 1:
    - Logger/Console delivery

    Phase 2:
    - Slack Webhook

    Phase 3:
    - Teams / Email / PagerDuty

    Responsibilities:
    - Format alerts
    - Deliver alerts
    - Update delivery status
    """

    def __init__(
        self,
        alert_repo: ChurnAlertRepository,
    ):
        self.alert_repo = alert_repo


    def dispatch_alert(
        self,
        alert: ChurnAlert,
    ) -> bool:

        alert_id = alert.alert_id

        logger.debug(
            "Dispatching alert | alert_id=%s",
            alert_id,
        )

        try:
            message = self._build_alert_message(
                alert
            )

            self._send(message)

            self._mark_delivery_success(
                alert_id
            )

            logger.info(
                "Alert dispatched successfully | alert_id=%s",
                alert_id,
            )

            return True

        except Exception:

            logger.exception(
                "Alert dispatch failed | alert_id=%s",
                alert_id,
            )

            self._mark_delivery_failed(
                alert_id
            )

            return False


    def _build_alert_message(
        self,
        alert: ChurnAlert,
    ) -> str:

        if alert.risk_reasons:
            reasons = "\n".join(
                f"• {reason}"
                for reason in alert.risk_reasons
            )
        else:
            reasons = "• No reasons available"

        if alert.severity == "urgent":
            icon = "🚨"
        elif alert.severity == "high":
            icon = "⚠️"
        else:
            icon = "ℹ️"

        return (
            f"\n"
            f"{icon} {alert.alert_type.replace('_', ' ')}\n"
            f"{'-' * 50}\n"
            f"Customer ID : {alert.customer_id}\n"
            f"Email       : {alert.customer_email or 'N/A'}\n"
            f"Tier        : {alert.tier}\n"
            f"Ticket ID   : {alert.ticket_id or 'N/A'}\n\n"
            f"Risk Score  : {alert.score}\n"
            f"Severity    : {alert.severity}\n\n"
            f"Reasons:\n"
            f"{reasons}\n"
            f"{'-' * 50}"
        )


    def _send(
        self,
        message: str,
    ) -> None:
        """
        Phase 1:
        Console/Logger

        Phase 2:
        Slack Webhook

        Phase 3:
        Teams / Email
        """

        logger.warning(
            "MOCK ALERT DELIVERY\n%s",
            message,
        )


    def _mark_delivery_success(
        self,
        alert_id: str,
    ) -> None:

        self.alert_repo.mark_delivery_sent(
            alert_id
        )

    def _mark_delivery_failed(
        self,
        alert_id: str,
    ) -> None:

        self.alert_repo.mark_delivery_failed(
            alert_id
        )