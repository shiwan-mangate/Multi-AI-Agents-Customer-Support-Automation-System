# crm_agent/adapters/faq_adapter.py

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


class FAQAdapter(BaseAdapter):
    """
    FAQ Agent -> CRMResolvedEvent adapter.
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
            "Adapting FAQ output | ticket_id=%s",
            ticket_id,
        )

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

        logger.warning(
            "GLOBAL query_intent = %s",
            global_context.get("query_intent"),
        )

        logger.warning(
            "EXECUTION query_intent = %s",
            agent_output.get("execution_metadata", {}).get("query_intent"),
        )

        logger.warning(
            "FINAL analytics.intent(before overwrite) = %s",
            analytics_meta.intent,
        )

        conversation_meta = (
            self._build_conversation_metadata(
                global_context
            )
        )

        raw_status = agent_output.get(
            "status",
            "resolved",
        )

        resolution_block = (
            agent_output.get(
                "resolution",
                {}
            )
        )

        clarification_block = (
            agent_output.get(
                "clarification",
                {}
            )
        )

        if raw_status == "clarification_required":

            resolution_type = (
                "clarification_requested"
            )

            resolution_message = (
                clarification_block.get(
                    "question",
                    "",
                )
            )

        else:

            raw_res_type = resolution_block.get("resolution_type", "unknown")
            
            if not raw_res_type or raw_res_type.lower() == "unknown":
                resolution_type = "faq_answer"
            else:
                resolution_type = raw_res_type

            resolution_message = resolution_block.get("message", "")

        crm_status = (
            "escalated"
            if raw_status == "handoff"
            else raw_status
        )

        resolution_meta = (
            ResolutionMetadata(
                status=crm_status,
                resolution_type=resolution_type,
                resolution_message=resolution_message,
                resolved_by=agent_output.get(
                    "audit",
                    {},
                ).get(
                    "handled_by",
                    "faq_agent",
                ),
                time_to_resolution_ms=agent_output.get("duration_ms")
            )
        )

        decisioning = (
            agent_output.get(
                "decisioning",
                {}
            )
        )

        knowledge_gap = bool(
            decisioning.get(
                "knowledge_gap_detected"
            )
        )

        escalation_required = bool(
            decisioning.get(
                "escalation_required"
            )
        )

        if knowledge_gap:

            decision_code = (
                "KNOWLEDGE_GAP"
            )

        elif escalation_required:

            decision_code = (
                "ESCALATION_REQUIRED"
            )

        elif raw_status == "clarification_required":

            decision_code = (
                "CLARIFICATION_REQUIRED"
            )

        else:

            decision_code = (
                "FAQ_CONFIDENT"
            )

        decision_meta = (
            DecisionMetadata(
                decision_code=decision_code,
                decision_reason=(
                    f"Confidence="
                    f"{decisioning.get('confidence_score', 0.0)}"
                ),
                review_required=(
                    escalation_required
                ),
            )
        )

        is_escalated = (
            escalation_required
            or knowledge_gap
        )

        if knowledge_gap:
            risk_level = "high"
        elif raw_status == "clarification_required":
            risk_level = "medium"
        else:
            risk_level = "low"

        risk_meta = RiskMetadata(
            escalated=is_escalated,
            security_flag=False,
            human_review_required=is_escalated,
            risk_level=risk_level,
        )

        execution_metadata = (
            agent_output.get(
                "execution_metadata",
                {}
            )
        )

        if execution_metadata.get(
            "query_intent"
        ):
            analytics_meta.intent = (
                execution_metadata[
                    "query_intent"
                ]
            )

        logger.warning(
            "FINAL analytics.intent(after overwrite) = %s",
            analytics_meta.intent,
        )

        logger.info(
            "FAQ output adapted successfully | ticket_id=%s",
            ticket_id,
        )

        return CRMResolvedEvent(
            event=event_meta,
            ticket=ticket_meta,
            customer=customer_meta,
            resolution=resolution_meta,
            risk=risk_meta,
            decision=decision_meta,
            analytics=analytics_meta,
            conversation=conversation_meta,
            financial=None,
        )