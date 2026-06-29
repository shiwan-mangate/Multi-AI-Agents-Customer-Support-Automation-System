# crm_agent/services/processing/event_router.py

import logging
from dataclasses import dataclass
from enum import Enum

from crm_agent.schemas.crm_event import CRMResolvedEvent


logger = logging.getLogger(__name__)


class PipelineRoute(str, Enum):
    FAQ = "faq_pipeline"
    REFUND = "refund_pipeline"
    ACCOUNT = "account_pipeline"
    ESCALATION = "escalation_pipeline"
    DEAD_LETTER = "dead_letter_pipeline"
    UNKNOWN = "unknown_pipeline"


@dataclass
class ExecutionPlan:
    """
    Deterministic execution contract returned by the router.
    """

    route: PipelineRoute

    is_terminal: bool

    persist_transcript: bool
    update_profile: bool
    run_churn_analysis: bool
    generate_alerts: bool

    failure_reason: str | None = None


class EventRouter:
    """
    Stateless deterministic routing layer.
    """

    def __init__(self):

        self.ROUTE_MAP = {
            "faq_agent": PipelineRoute.FAQ,
            "refund_agent": PipelineRoute.REFUND,
            "account_agent": PipelineRoute.ACCOUNT,
            "escalation_agent": PipelineRoute.ESCALATION,
        }

        self.TERMINAL_STATES = {
            "resolved",
            "failed",
            "denied",
            "escalated",
            "closed",
            "duplicate_suppressed",
        }


    def build_processing_plan(
        self,
        event: CRMResolvedEvent
    ) -> ExecutionPlan:

        try:
            route = self._resolve_pipeline(event)

            self._validate_route(
                event=event,
                route=route,
            )

            is_terminal = self._is_terminal_event(event)

            plan = ExecutionPlan(
                route=route,
                is_terminal=is_terminal,

                persist_transcript=self._requires_transcript_persistence(
                    event
                ),

                update_profile=self._requires_profile_update(
                    event=event,
                    is_terminal=is_terminal,
                ),

                run_churn_analysis=self._requires_churn_analysis(
                    event=event,
                    is_terminal=is_terminal,
                ),

                generate_alerts=self._requires_alert_generation(
                    event
                ),
            )

            logger.info(
                "Execution plan created | event_id=%s | route=%s",
                event.event.event_id,
                route.value,
            )

            return plan

        except ValueError as e:

            logger.warning(
                "Routing validation failed | event_id=%s | error=%s",
                event.event.event_id,
                str(e),
            )

            return self._handle_unknown_route(
                reason=str(e)
            )


    def _resolve_pipeline(
        self,
        event: CRMResolvedEvent
    ) -> PipelineRoute:

        source_agent = event.event.source_agent

        return self.ROUTE_MAP.get(
            source_agent,
            PipelineRoute.UNKNOWN,
        )

    def _validate_route(
        self,
        event: CRMResolvedEvent,
        route: PipelineRoute,
    ) -> None:

        if route == PipelineRoute.UNKNOWN:
            raise ValueError(
                f"Unknown source_agent: "
                f"{event.event.source_agent}"
            )

        resolution_type = (
            event.resolution.resolution_type
        )

        if route == PipelineRoute.REFUND:

            valid_refund_types = {
                "refund_completed",
                "refund_rejected",
                "idempotent_replay",
            }

            if resolution_type not in valid_refund_types:
                raise ValueError(
                    f"Invalid refund resolution_type: "
                    f"{resolution_type}"
                )

        if route == PipelineRoute.FAQ:

            valid_faq_types = {
                "faq_answer",
                "knowledge_gap",
                "system_failure",
                "clarification_requested",
            }

            if resolution_type not in valid_faq_types:
                raise ValueError(
                    f"Invalid FAQ resolution_type: "
                    f"{resolution_type}"
                )


    def _is_terminal_event(
        self,
        event: CRMResolvedEvent
    ) -> bool:

        return (
            event.resolution.status
            in self.TERMINAL_STATES
        )

    def _requires_transcript_persistence(
        self,
        event: CRMResolvedEvent
    ) -> bool:

        internal_agents = {
            "retry_worker",
            "system_monitor",
        }

        return (
            event.event.source_agent
            not in internal_agents
        )

    def _requires_profile_update(
        self,
        event: CRMResolvedEvent,
        is_terminal: bool,
    ) -> bool:

        return is_terminal

    def _requires_churn_analysis(
        self,
        event: CRMResolvedEvent,
        is_terminal: bool,
    ) -> bool:

        if not is_terminal:
            return False

        sentiment = (
            event.analytics.sentiment_end
            if event.analytics
            else None
        )

        status = event.resolution.status

        if sentiment in ["frustrated", "angry"]:
            return True

        if status in [
            "failed",
            "denied",
            "escalated",
        ]:
            return True

        return False

    def _requires_alert_generation(
        self,
        event: CRMResolvedEvent
    ) -> bool:

        sentiment = (
            event.analytics.sentiment_end
            if event.analytics
            else None
        )

        status = event.resolution.status

        if status in ["failed", "escalated"]:
            return True

        if sentiment == "angry":
            return True

        if (
            event.customer.tier
            in ["enterprise", "premium"]
            and sentiment == "frustrated"
        ):
            return True

        return False


    def _handle_unknown_route(
        self,
        reason: str
    ) -> ExecutionPlan:

        return ExecutionPlan(
            route=PipelineRoute.DEAD_LETTER,

            is_terminal=True,

            persist_transcript=False,
            update_profile=False,
            run_churn_analysis=False,
            generate_alerts=False,

            failure_reason=reason,
        )