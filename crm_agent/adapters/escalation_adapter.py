# crm_agent/adapters/escalation_adapter.py

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


class EscalationAdapter(BaseAdapter):
    """
    Escalation Agent -> CRMResolvedEvent adapter.
    """

    def to_crm_event(
        self,
        agent_output: Dict[str, Any],
        global_context: Dict[str, Any],
    ) -> CRMResolvedEvent:

        ticket_id = agent_output.get("ticket_id", "UNKNOWN")
        logger.debug("Adapting Escalation output | ticket_id=%s", ticket_id)

        event_meta = self._build_event_metadata(agent_output)
        
        # 🟢 FIX 1: Force identity so the CRM Router doesn't DEAD-LETTER the event!
        event_meta.source_agent = "escalation_agent"
        event_meta.event_type = "ticket.escalated"

        ticket_meta = self._build_ticket_metadata(agent_output, global_context)
        customer_meta = self._build_customer_metadata(global_context)
        analytics_meta = self._build_analytics_metadata(global_context)
        conversation_meta = self._build_conversation_metadata(global_context)

        response_block = agent_output.get("response", {})

        # 🟢 FIX 2: Dig into the response block to get the true escalation status
        raw_status = response_block.get("status") or agent_output.get("status", "FAILED")
        raw_status = str(raw_status).upper()

        status_mapping = {
            "ESCALATED": "escalated",
            "DUPLICATE_SUPPRESSED": "duplicate_suppressed",
            "HUMAN_REVIEW_REQUIRED": "human_review_required",
            "COMPLETED": "escalated", # Fallback safety
            "FAILED": "failed",
        }

        crm_status = status_mapping.get(raw_status, "failed")
        assigned_team = response_block.get("assigned_team", "general_support")
        case_id = response_block.get("case_id") or agent_output.get("case_id")

        if crm_status == "escalated":
            resolution_type = "escalation_created"
            resolution_message = f"Escalation case {case_id} created."
        elif crm_status == "duplicate_suppressed":
            resolution_type = "duplicate_escalation"
            resolution_message = "Existing escalation reused."
        elif crm_status == "human_review_required":
            resolution_type = "awaiting_human_review"
            resolution_message = "Escalation paused pending review."
        else:
            resolution_type = "escalation_failed"
            resolution_message = agent_output.get("error", "Automated escalation failed.")

        resolution_meta = ResolutionMetadata(
            status=crm_status,
            resolution_type=resolution_type,
            resolution_message=resolution_message,
            resolved_by="escalation_agent",
            time_to_resolution_ms=agent_output.get("duration_ms")
        )

        if crm_status == "escalated":
            decision_code = "ESCALATION_CREATED"
            decision_reason = f"Assigned to {assigned_team}"
        elif crm_status == "duplicate_suppressed":
            decision_code = "DUPLICATE_SUPPRESSED"
            decision_reason = "Existing active case reused"
        elif crm_status == "human_review_required":
            decision_code = "HUMAN_REVIEW_REQUIRED"
            decision_reason = "Governance policy triggered"
        else:
            decision_code = "ESCALATION_FAILED"
            decision_reason = agent_output.get("error", "Internal failure")

        decision_meta = DecisionMetadata(
            decision_code=decision_code,
            decision_reason=decision_reason,
            review_required=(crm_status == "human_review_required"),
        )

        risk_level = "urgent" if crm_status == "human_review_required" else "high"

        risk_meta = RiskMetadata(
            escalated=True,
            security_flag=False,
            human_review_required=(crm_status == "human_review_required"),
            risk_level=risk_level,
        )

        if analytics_meta:
            if "escalation" not in analytics_meta.issue_tags:
                analytics_meta.issue_tags.append("escalation")
            if assigned_team and assigned_team not in analytics_meta.issue_tags:
                analytics_meta.issue_tags.append(assigned_team)

        logger.info(
            "Escalation output adapted successfully | ticket_id=%s | status=%s",
            ticket_id, crm_status,
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