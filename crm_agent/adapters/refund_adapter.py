# crm_agent/adapters/refund_adapter.py

import logging
from decimal import Decimal
from typing import Dict, Any

from crm_agent.adapters.base_adapter import BaseAdapter

from crm_agent.schemas.crm_event import (
    CRMResolvedEvent,
    ResolutionMetadata,
    DecisionMetadata,
    RiskMetadata,
    FinancialMetadata,
)

logger = logging.getLogger(__name__)


class RefundAdapter(BaseAdapter):
    """
    Refund Agent -> CRMResolvedEvent adapter.
    """

    def to_crm_event(
        self,
        agent_output: Dict[str, Any],
        global_context: Dict[str, Any],
    ) -> CRMResolvedEvent:
        
        logger.warning(
            "REFUND ADAPTER INPUT | customer_id=%s | ltv=%s",
            global_context.get("customer_id"),
            global_context.get("ltv"),
        )
        ticket_id = agent_output.get(
            "ticket_id",
            "UNKNOWN",
        )

        logger.debug(
            "Adapting Refund output | ticket_id=%s",
            ticket_id,
        )
        agent_output["source_agent"] = "refund_agent"
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

        execution_metadata = agent_output.get(
            "execution_metadata",
            {}
        )

        analytics_meta.intent = (
            execution_metadata.get("query_intent")
            or global_context.get("query_intent")
            or analytics_meta.intent
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

        crm_status = (
            "denied"
            if raw_status == "closed"
            else raw_status
        )

        resolution_block = (
            agent_output.get(
                "resolution",
                {}
            )
        )


        resolution_meta = (
            ResolutionMetadata(
                status=crm_status,
                resolution_type=resolution_block.get(
                    "resolution_type",
                    "refund_completed",
                ),
                resolution_message=resolution_block.get(
                    "message",
                    "",
                ),
                resolved_by=agent_output.get(
                    "assigned_agent",
                    "refund_agent",
                ),
                time_to_resolution_ms=agent_output.get("duration_ms")
            )
        )

        decision_block = (
            agent_output.get(
                "decision",
                {}
            )
        )

        audit_block = (
            agent_output.get(
                "audit",
                {}
            )
        )

        review_required = bool(
            audit_block.get(
                "review_required",
                False,
            )
        )

        decision_meta = (
            DecisionMetadata(
                decision_code=decision_block.get(
                    "decision_code",
                    "UNKNOWN",
                ),
                decision_reason=decision_block.get(
                    "decision_reason",
                    "",
                ),
                review_required=review_required,
            )
        )

        financial_meta = None

        # Syntax Fix: Cleaned up the 'is not not None' double-negative structural typo
        if resolution_block.get("refund_amount") is not None:
            financial_meta = (
                FinancialMetadata(
                    refund_amount=Decimal(
                        str(
                            resolution_block.get(
                                "refund_amount",
                                0,
                            )
                        )
                    ),
                    currency=resolution_block.get(
                        "currency",
                        "USD",
                    ),
                    transaction_id=resolution_block.get(
                        "transaction_id"
                    ),
                )
            )

        is_failed = (
            crm_status == "failed"
        )

        if is_failed:
            risk_level = "high"
        elif review_required:
            risk_level = "medium"
        else:
            risk_level = "low"

        risk_meta = RiskMetadata(
            escalated=is_failed,
            security_flag=False,
            human_review_required=review_required,
            risk_level=risk_level,
        )

        if (
            "refund"
            not in analytics_meta.issue_tags
        ):
            analytics_meta.issue_tags.append(
                "refund"
            )

        logger.info(
            "Refund output adapted successfully | ticket_id=%s",
            ticket_id,
        )

        return CRMResolvedEvent(
            event=event_meta,
            ticket=ticket_meta,
            customer=customer_meta,
            resolution=resolution_meta,
            risk=risk_meta,
            financial=financial_meta,
            decision=decision_meta,
            analytics=analytics_meta,
            conversation=conversation_meta,
        )