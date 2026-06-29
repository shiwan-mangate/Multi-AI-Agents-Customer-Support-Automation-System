# crm_agent/services/processing/pipeline_executor.py

import logging
from typing import Optional

from crm_agent.schemas.crm_event import CRMResolvedEvent
from crm_agent.schemas.churn import ChurnAssessment
from crm_agent.services.processing.event_router import ExecutionPlan

from crm_agent.services.transcript.transcript_service import (
    TranscriptService,
)
from crm_agent.services.customer.profile_service import (
    ProfileService,
)
from crm_agent.services.churn.churn_service import (
    ChurnService,
)
from crm_agent.services.alerts.alert_service import (
    AlertService,
)

logger = logging.getLogger(__name__)


class PipelineExecutor:
    """
    Pure orchestration layer.

    Responsibilities:
    - Execute workflow steps in the correct order.
    - Coordinate service execution.
    - Never contain business logic.
    - Never execute SQL directly.
    - Never commit or rollback transactions.

    Transaction ownership belongs to EventProcessor.
    """

    def __init__(
        self,
        transcript_service: TranscriptService,
        profile_service: ProfileService,
        churn_service: ChurnService,
        alert_service: AlertService,
    ):
        self.transcript_service = transcript_service
        self.profile_service = profile_service
        self.churn_service = churn_service
        self.alert_service = alert_service

    def execute_plan(
        self,
        event: CRMResolvedEvent,
        plan: ExecutionPlan,
    ) -> None:

        logger.debug(
            "Executing pipeline | event_id=%s",
            event.event.event_id,
        )

        if plan.persist_transcript:
            logger.debug(
                "Transcript step enabled | ticket_id=%s",
                event.ticket.ticket_id,
            )
            self.transcript_service.create_transcript(
                event
            )

        if plan.update_profile:
            logger.debug(
                "Profile step enabled | customer_id=%s",
                event.customer.customer_id,
            )
            self.profile_service.update_customer_profile(
                event
            )

        assessment: Optional[ChurnAssessment] = None

        if plan.run_churn_analysis:
            logger.debug(
                "Churn analysis enabled | customer_id=%s",
                event.customer.customer_id,
            )
            assessment = (
                self.churn_service.analyze_customer_risk(
                    event
                )
            )

        if (
            plan.generate_alerts
            and assessment is not None
        ):
            logger.debug(
                "Alert generation enabled | customer_id=%s",
                event.customer.customer_id,
            )
            self.alert_service.create_alert_if_needed(
                event=event,
                assessment=assessment,
            )

        logger.info(
            "Pipeline execution completed | event_id=%s",
            event.event.event_id,
        )