# crm_agent/adapters/base_adapter.py

import logging
import uuid
from abc import ABC, abstractmethod
from decimal import Decimal
from typing import Any, Dict

from crm_agent.schemas.crm_event import (
    CRMResolvedEvent,
    EventMetadata,
    TicketMetadata,
    CustomerMetadata,
    ConversationMetadata,
    AnalyticsMetadata,
)

logger = logging.getLogger(__name__)


class BaseAdapter(ABC):
    """
    Shared adapter utilities for all specialist agents.

    Child adapters:
        FAQAdapter
        RefundAdapter
        AccountAdapter
        EscalationAdapter
    """

    SCHEMA_VERSION = "1.0.0"

    @abstractmethod
    def to_crm_event(
        self,
        agent_output: Dict[str, Any],
        global_context: Dict[str, Any],
    ) -> CRMResolvedEvent:
        pass


    def _build_event_metadata(
        self,
        agent_output: Dict[str, Any],
        event_type: str = "ticket.resolved",
    ) -> EventMetadata:
        
        # Robust fallback for LLM variations in agent naming
        source_agent = (
            agent_output.get("assigned_agent")
            or agent_output.get("agent")
            or agent_output.get("source_agent")
            or "unknown_agent"
        )
        

        return EventMetadata(
            event_id=f"evt_{uuid.uuid4().hex}",
            event_type=event_type,
            source_agent=source_agent,
            schema_version=self.SCHEMA_VERSION,
        )

    def _build_ticket_metadata(
        self,
        agent_output: Dict[str, Any],
        global_context: Dict[str, Any],
    ) -> TicketMetadata:
        raw_ticket_id = agent_output.get("ticket_id") or global_context.get("ticket_id", "unknown")
        return TicketMetadata(
            ticket_id=str(raw_ticket_id)
        )


    def _build_customer_metadata(
        self,
        global_context: Dict[str, Any],
    ) -> CustomerMetadata:
        

        raw_customer_id = global_context.get("customer_id")

        logger.warning(
        "CRM EVENT BUILD | customer=%s | ltv=%s",
        raw_customer_id,
        global_context.get("ltv")
    )
        if raw_customer_id is None:
            raise ValueError(
                "customer_id missing from global_context"
            )

        # Inconsistency Fix: Updated fields to match customer_email and enforced Decimal ltv mapping
        return CustomerMetadata(
            customer_id=int(raw_customer_id),
            customer_email=global_context.get("customer_email"),
            tier=global_context.get("tier", "standard"),
            ltv=Decimal(str(global_context.get("ltv", "0.00"))),
        )


    def _build_analytics_metadata(
        self,
        global_context: Dict[str, Any],
    ) -> AnalyticsMetadata:
        logger.warning(
        "ADAPTER INTENT = %s",
        global_context.get("query_intent")
    )
        return AnalyticsMetadata(
            intent=global_context.get(
                "query_intent",
                "unknown",
            ),
            issue_tags=global_context.get(
                "issue_tags",
                [],
            ),
            sentiment_start=global_context.get(
                "sentiment_start",
                "neutral",
            ),
            sentiment_end=global_context.get(
                "sentiment_end",
                global_context.get(
                    "sentiment_start",
                    "neutral",
                ),
            ),
            language=global_context.get(
                "language",
                "en",
            ),
        )

    def _build_conversation_metadata(
        self,
        global_context: Dict[str, Any],
    ) -> ConversationMetadata:

        raw_messages = global_context.get(
            "conversation_history",
            [],
        )

        messages = []
        for msg in raw_messages:
            messages.append(
                {
                    "role": msg.get("role", "unknown"),
                    "content": msg.get("content", ""),
                    "timestamp": msg.get("timestamp"),
                }
            )
            
        return ConversationMetadata(
            messages=messages
        )