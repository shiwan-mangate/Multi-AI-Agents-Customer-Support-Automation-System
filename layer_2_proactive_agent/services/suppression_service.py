from datetime import datetime, timedelta, UTC
from typing import Tuple, Optional, Union

from layer_2_proactive_agent.repositories.proactive_outreach_repository import (
    ProactiveOutreachRepository,
)
from layer_2_proactive_agent.database.model.proactive_outreach_record import (
    ProactiveOutreachRecord,
)
from layer_2_proactive_agent.schemas.enums import (
    SignalType,
    OutreachStatus,
)
from layer_2_proactive_agent.utils.logger import logger

SUPPRESSION_WINDOWS = {
    SignalType.INACTIVE_CUSTOMER: 30,
    SignalType.HIGH_CHURN_RISK: 14,
    SignalType.RECENT_NEGATIVE_EXPERIENCE: 14,
    SignalType.VIP_RETENTION_RISK: 7,
}


class SuppressionService:
    """
    Business rules for suppression
    and outreach registry management.
    """

    def __init__(
        self,
        repo: ProactiveOutreachRepository,
    ):
        self.repo = repo

    def should_suppress(
        self,
        customer_id: int,
        signal_type: SignalType,
    ) -> Tuple[bool, Optional[str]]:
        """
        Checks if a customer has already been contacted for a given signal type
        within its active suppression cooling-off window.
        """
        signal_value = signal_type.value if isinstance(signal_type, SignalType) else str(signal_type)

        logger.info(
            "Status=START | Operation=SUPPRESSION_CHECK | Customer=%s | Signal=%s",
            customer_id,
            signal_value,
        )

        record = self.repo.already_contacted(
            customer_id=customer_id,
            signal_type=signal_value,
        )

        if record:
            logger.info(
                "Status=SUPPRESSED | RecordId=%s | Customer=%s | Signal=%s",
                record.id,
                customer_id,
                signal_value,
            )
            return True, record.id

        logger.info(
            "Status=NOT_SUPPRESSED | Customer=%s | Signal=%s",
            customer_id,
            signal_value,
        )
        return False, None

    def calculate_expiry(
        self,
        signal_type: SignalType,
    ) -> datetime:
        """
        Calculates when a suppression cooldown window will expire based on the signal type.
        """
        # Defensive check if signal_type comes in as a string value instead of the enum object
        if isinstance(signal_type, str):
            try:
                signal_type = SignalType(signal_type)
            except ValueError:
                raise ValueError(f"Unknown signal type string value: {signal_type}")

        days = SUPPRESSION_WINDOWS[signal_type]
        expiry = datetime.now(UTC) + timedelta(days=days)

        logger.info(
            "Status=EXPIRY_CALCULATED | Signal=%s | Days=%s | Expiry=%s",
            signal_type.value,
            days,
            expiry.isoformat(),
        )
        return expiry

    def create_outreach_record(
        self,
        workflow_id: str,
        signal_id: str,
        customer_id: int,
        signal_type: SignalType,
        decision: str,
    ) -> ProactiveOutreachRecord:
        """
        Factory method to construct an outreach tracking row for database persistence.
        """
        signal_value = signal_type.value if isinstance(signal_type, SignalType) else str(signal_type)

        logger.info(
            "Status=CREATE_OUTREACH_RECORD | Workflow=%s | Customer=%s | Signal=%s",
            workflow_id,
            customer_id,
            signal_value,
        )

        return ProactiveOutreachRecord(
            workflow_id=workflow_id,
            signal_id=signal_id,
            customer_id=customer_id,
            signal_type=signal_value,
            decision=decision,
            status=OutreachStatus.OUTREACH_CREATED.value,
            expires_at=self.calculate_expiry(signal_type),
        )

    def create_suppression_record(
        self,
        workflow_id: str,
        signal_id: str,
        customer_id: int,
        signal_type: SignalType,
    ) -> ProactiveOutreachRecord:
        """
        Factory method to construct an early abort/suppression row for audit tracking.
        """
        signal_value = signal_type.value if isinstance(signal_type, SignalType) else str(signal_type)

        logger.info(
            "Status=CREATE_SUPPRESSION_RECORD | Workflow=%s | Customer=%s | Signal=%s",
            workflow_id,
            customer_id,
            signal_value,
        )

        return ProactiveOutreachRecord(
            workflow_id=workflow_id,
            signal_id=signal_id,
            customer_id=customer_id,
            signal_type=signal_value,
            decision="SUPPRESSED",
            status=OutreachStatus.SUPPRESSED.value,
            expires_at=self.calculate_expiry(signal_type),
        )

    def save_outreach(
        self,
        record: ProactiveOutreachRecord,
    ) -> ProactiveOutreachRecord:
        """
        Routes the active outreach record to the database repository layer.
        """
        logger.info(
            "Status=PERSIST_OUTREACH | Workflow=%s",
            record.workflow_id,
        )
        return self.repo.record_outreach(record)

    def save_suppression(
        self,
        record: ProactiveOutreachRecord,
    ) -> ProactiveOutreachRecord:
        """
        Routes the early abort tracking record to the database repository layer.
        """
        logger.info(
            "Status=PERSIST_SUPPRESSION | Workflow=%s",
            record.workflow_id,
        )
        return self.repo.record_suppression(record)