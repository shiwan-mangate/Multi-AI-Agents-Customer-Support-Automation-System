# crm_agent/adapters/account_adapter.py

import logging
from typing import Dict, Any

from crm_agent.adapters.base_adapter import BaseAdapter
from crm_agent.schemas.crm_event import (
    CRMResolvedEvent,
    ResolutionMetadata,
    DecisionMetadata,
    RiskMetadata,
)

logger = logging.getLogger(__name__)


class AccountAdapter(BaseAdapter):
    """
    Account Agent -> CRMResolvedEvent adapter.

    Converts Account Agent business outcomes into the
    canonical CRMResolvedEvent contract.
    """

    def to_crm_event(
        self,
        agent_output: Dict[str, Any],
        global_context: Dict[str, Any],
    ) -> CRMResolvedEvent:

        ticket_id = agent_output.get(
            "ticket_id",
            "UNKNOWN",
        )

        logger.debug(
            "Adapting Account Agent output | ticket_id=%s",
            ticket_id,
        )

        agent_output["source_agent"] = "account_agent"
        event_meta = self._build_event_metadata(
            agent_output
        )

        ticket_meta = self._build_ticket_metadata(
            agent_output,
            global_context,
        )

        customer_meta = self._build_customer_metadata(
            global_context
        )

        analytics_meta = self._build_analytics_metadata(
            global_context
        )

        conversation_meta = (
            self._build_conversation_metadata(
                global_context
            )
        )

        raw_status = agent_output.get(
            "status",
            "completed",
        )

        status_mapping = {
            "completed": "resolved",
            "escalated": "escalated",
            "denied": "denied",
            "clarification_required": "clarification_required",
            "failed": "failed",
        }

        crm_status = status_mapping.get(
            raw_status,
            "failed",
        )

        request_block = agent_output.get(
            "request",
            {},
        )

        requested_action = request_block.get(
            "requested_action"
        )

        customer_response = agent_output.get(
            "customer_response",
            "",
        )

        if crm_status == "clarification_required":

            resolution_type = (
                "clarification_requested"
            )

            resolution_message = (
                customer_response
                or "Could you provide more details?"
            )

        elif crm_status == "escalated":

            resolution_type = (
                "security_escalation"
            )

            resolution_message = (
                customer_response
            )

        else:

            resolution_type = (
                requested_action
                or "account_action"
            )

            resolution_message = (
                customer_response
            )

        resolution_meta = (
            ResolutionMetadata(
                status=crm_status,
                resolution_type=resolution_type,
                resolution_message=resolution_message,
                resolved_by=agent_output.get(
                    "agent",
                    "account_agent",
                ),
                time_to_resolution_ms=agent_output.get("duration_ms"),
            )
        )

        decision_block = agent_output.get(
            "decision",
            {},
        )

        verification_level = (
            decision_block.get(
                "verification_level"
            )
        )

        if crm_status == "escalated":

            decision_code = (
                "SECURITY_ESCALATION"
            )

        elif crm_status == "denied":

            decision_code = (
                "DENIED_BY_POLICY"
            )

        elif crm_status == "clarification_required":

            decision_code = (
                "CLARIFICATION_REQUIRED"
            )

        else:

            decision_code = (
                requested_action.upper()
                if requested_action
                else "ACCOUNT_ACTION"
            )

        decision_meta = (
            DecisionMetadata(
                decision_code=decision_code,
                decision_reason=decision_block.get(
                    "decision_reason",
                    "",
                ),
                verification_level=verification_level,
                review_required=(
                    crm_status == "escalated"
                ),
            )
        )

        agent_risk_level = (
            decision_block.get(
                "risk_level",
                "LOW",
            ).upper()
        )

        is_security_escalation = (
            crm_status == "escalated"
            and agent_risk_level == "CRITICAL"
        )

        is_system_failure = (
            crm_status == "failed"
        )

        if is_security_escalation:
            risk_level = "urgent"
        elif is_system_failure:
            risk_level = "high"
        elif crm_status == "clarification_required":
            risk_level = "medium"
        else:
            risk_level = "low"

        risk_meta = RiskMetadata(
            escalated=(
                crm_status == "escalated"
                or is_system_failure
            ),
            security_flag=is_security_escalation,
            human_review_required=(
                crm_status == "escalated"
            ),
            risk_level=risk_level,
        )

        if analytics_meta:

            if (
                "account"
                not in analytics_meta.issue_tags
            ):
                analytics_meta.issue_tags.append(
                    "account"
                )

            if (
                requested_action
                and requested_action
                not in analytics_meta.issue_tags
            ):
                analytics_meta.issue_tags.append(
                    requested_action
                )

        logger.info(
            "Account output adapted successfully | "
            "ticket_id=%s | action=%s | status=%s",
            ticket_id,
            requested_action,
            crm_status,
        )

        return CRMResolvedEvent(
            event=event_meta,
            ticket=ticket_meta,
            customer=customer_meta,
            resolution=resolution_meta,
            risk=risk_meta,
            financial=None,
            decision=decision_meta,
            analytics=analytics_meta,
            conversation=conversation_meta,
        )