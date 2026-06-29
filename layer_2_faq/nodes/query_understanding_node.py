from datetime import datetime, UTC
from typing import Dict, Any

from ..schemas.faq_state import FAQState
from ..schemas.faq_models import AttemptRecord
from ..services.query_rewriter import QueryRewriterService
from layer_2_faq.llm import create_llm

import logging
logger = logging.getLogger(__name__)


llm = create_llm()
rewriter_service = QueryRewriterService(llm=llm)


def query_understanding_node(
    state: FAQState
) -> Dict[str, Any]:
    """
    Rewrites customer query into structured retrieval query.
    Supports clarification loop context.
    """
    logger.warning("========== ENTERED QUERY UNDERSTANDING NODE ==========")
    now = datetime.now(UTC)

    ticket = state.get("ticket", {})
    message_raw = ticket.get("message_raw", "")

    clarification_response = state.get(
        "clarification_response"
    )

    if clarification_response:
        message_raw = (
            f"{message_raw}\n\n"
            f"Customer clarification: "
            f"{clarification_response}"
        )

    retry_count = state.get(
        "retry_count",
        0
    )

    try:
        output = rewriter_service.rewrite_query(
            message_raw=message_raw,
            entities=state.get("entities", {}),
            order_context=state.get("order_context"),
            customer_tier=state.get(
                "customer_tier",
                "standard"
            ),
            retry_count=retry_count,
            correction_note=state.get(
                "clarification_response"
            )
        )

        logger.warning(output)
        logger.warning(type(output))
        logger.warning(output.model_dump())

        logger.warning(
        f"REWRITTEN QUERY = {output.rewritten_query}"
        )

        logger.warning(
            f"QUERY INTENT = {output.query_intent}"
        )

        logger.warning(
            f"AMBIGUOUS = {output.is_ambiguous}"
        )

        attempt = AttemptRecord(
            attempt_number=retry_count + 1,
            rewritten_query=output.rewritten_query,
            timestamp=now
        )
        logger.warning("=" * 60)
        logger.warning("RETURNING FROM QUERY UNDERSTANDING")
        logger.warning(f"ambiguity = {output.is_ambiguous}")
        logger.warning("=" * 60)

        return {
            "rewritten_query": output.rewritten_query,
            "query_intent": output.query_intent,
            "ambiguity_detected": output.is_ambiguous,
            "attempt_history": [
                attempt.model_dump()
            ],
            "current_node": "query_understanding_node",
            "updated_at": now,
            "workflow_logs": [{
                "timestamp": now.isoformat(),
                "node": "query_understanding_node",
                "message": (
                    "Query understanding "
                    "completed successfully."
                ),
                "data": {
                    "ticket_id": state.get(
                        "ticket_id"
                    ),
                    "attempt_number": retry_count + 1,
                    "rewritten_query": output.rewritten_query,
                    "query_intent": output.query_intent,
                    "is_ambiguous": output.is_ambiguous
                }
            }]
        }

    except Exception as e:
        error_msg = str(e)

        return {
            "escalation_required": True,
            "escalation_reason": (
                f"Query understanding failed: "
                f"{error_msg}"
            ),
            "decision_target": "escalation_agent",
            "errors": [error_msg]
        }