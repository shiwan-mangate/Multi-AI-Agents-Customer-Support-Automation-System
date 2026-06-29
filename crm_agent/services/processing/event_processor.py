# crm_agent/services/processing/event_processor.py

import logging
from sqlalchemy.orm import Session
from crm_agent.services.processing.event_router import (EventRouter, PipelineRoute)
from crm_agent.schemas.crm_event import CRMResolvedEvent
from crm_agent.services.ingestion.idempotency_service import (IdempotencyService)
from crm_agent.services.churn.churn_engine import (ChurnEngine)

# Inconsistency Fix: Pointed import statement to the correct repository file name
from crm_agent.repositories.customer_event_repository import (CRMEventRepository)
from crm_agent.repositories.transcript_repository import (TranscriptRepository)
from crm_agent.repositories.customer_profile_repository import (CustomerProfileRepository)
from crm_agent.repositories.churn_alert_repository import (ChurnAlertRepository)


logger = logging.getLogger(__name__)


class EventProcessor:
    """
    Core execution pipeline orchestrator for incoming resolved agent messages.
    """
    def __init__(
        self,
        session: Session,
        router: EventRouter,
        idempotency_service: IdempotencyService,
        churn_engine: ChurnEngine,
        event_repo: CRMEventRepository,
        transcript_repo: TranscriptRepository,
        profile_repo: CustomerProfileRepository,
        alert_repo: ChurnAlertRepository,
    ):
        self.session = session
        self.router = router
        self.idempotency = idempotency_service
        self.churn_engine = churn_engine
        self.event_repo = event_repo
        self.transcript_repo = transcript_repo
        self.profile_repo = profile_repo
        self.alert_repo = alert_repo

    def process_event(
        self,
        event: CRMResolvedEvent
    ) -> None:

        event_id = event.event.event_id

        logger.info(
            "Processing started | event_id=%s",
            event_id,
        )

        if self.idempotency.is_duplicate_event(event):
            logger.warning(
                "Duplicate event skipped | event_id=%s",
                event_id,
            )

            self.event_repo.mark_done(event_id)
            try:
                self.session.commit()
            except Exception:
                self.session.rollback()
                raise
            return

        plan = self.router.build_processing_plan(event)

        if plan.route == PipelineRoute.DEAD_LETTER:
            logger.error(
                "Dead letter routing | event_id=%s | reason=%s",
                event_id,
                plan.failure_reason,
            )

            self.session.rollback()
            self.event_repo.mark_dead(
                event_id=event_id,
                final_error=plan.failure_reason or "Unknown route",
            )
            self.idempotency.mark_dead(event)
            try:
                self.session.commit()
            except Exception:
                self.session.rollback()
                raise
            return

        try:
            if plan.persist_transcript:
                logger.warning("CHECKPOINT A")
                transcript = self.transcript_repo.get_by_ticket_id(
                    event.ticket.ticket_id
                )

                if transcript:
                    logger.warning("CHECKPOINT B")
                    logger.info(
                        "Updating transcript | ticket_id=%s",
                        event.ticket.ticket_id,
                    )

                    self.transcript_repo.update_transcript(
                        transcript=transcript,
                        event=event,
                    )

                else:
                    logger.info(
                        "Creating transcript | ticket_id=%s",
                        event.ticket.ticket_id,
                    )
                    logger.warning("CHECKPOINT C")
                    self.transcript_repo.create_transcript(
                        event
                    )

            if plan.update_profile:
                self.profile_repo.upsert_profile_from_event(
                    event
                )

            if plan.run_churn_analysis:
                # Safely accesses exact 64-bit bigint routing representations via standard Python int
                profile = self.profile_repo.get_profile(
                    event.customer.customer_id
                )

                if profile is None:
                    raise ValueError(
                        "Customer profile missing after UPSERT"
                    )

                assessment = (
                    self.churn_engine.calculate_churn_risk(
                        profile=profile,
                        event=event,
                    )
                )

                # Updates churn state safely passing the refactored Decimal numbers
                self.profile_repo.update_churn_state(
                    customer_id=profile.customer_id,
                    new_score=assessment.churn_score,
                    new_level=assessment.churn_level,
                )

                if (
                    plan.generate_alerts
                    and assessment.churn_level
                    in ["high", "urgent"]
                ):
                    self._handle_alerts(
                        event=event,
                        assessment=assessment,
                    )

            self.idempotency.mark_success(event)
            self.event_repo.mark_done(event_id)
            try:
                self.session.commit()
            except Exception:
                self.session.rollback()
                raise

            logger.info(
                "Processing completed | event_id=%s",
                event_id,
            )

        except Exception as e:
            logger.exception(
                "Processing failed | event_id=%s | error=%s",
                event_id,
                str(e),
            )

            self.session.rollback()

            try:
                self.event_repo.mark_failed(
                    event_id=event_id,
                    error_msg=str(e),
                )
                try:
                    self.session.commit()
                except Exception:
                    self.session.rollback()
                    raise

            except Exception as queue_error:
                self.session.rollback()
                logger.critical(
                    "Queue state update failed | event_id=%s | error=%s",
                    event_id,
                    str(queue_error),
                )
                raise


    def _handle_alerts(
        self,
        event: CRMResolvedEvent,
        assessment,
    ) -> None:

        alert_type = (
            "VIP_CHURN_RISK"
            if event.customer.tier in ["enterprise", "premium"]
            else "CHURN_RISK"
        )

        existing_alert = (
            self.alert_repo.get_open_alert(
                customer_id=event.customer.customer_id,
                alert_type=alert_type,
            )
        )

        if existing_alert:
            logger.info(
                "Alert suppressed | customer_id=%s | type=%s",
                event.customer.customer_id,
                alert_type,
            )
            return

        self.alert_repo.create_alert(
            customer_id=event.customer.customer_id,
            alert_type=alert_type,
            severity=("CRITICAL"
            if assessment.churn_level == "urgent"
            else assessment.churn_level.upper()),
            score=assessment.churn_score,
            reason=(
                f"{alert_type} detected "
                f"at score {assessment.churn_score}"
            ),
            risk_reasons=assessment.risk_reasons,
            tier=event.customer.tier,
            ticket_id=event.ticket.ticket_id,
            customer_email=event.customer.customer_email,
            source_agent=event.event.source_agent,
        )

        logger.warning(
            "Alert created | customer_id=%s | alert_type=%s",
            event.customer.customer_id,
            alert_type,
        )