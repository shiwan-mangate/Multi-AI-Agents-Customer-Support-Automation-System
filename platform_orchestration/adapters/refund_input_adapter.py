# platform_orchestration/adapters/refund_input_adapter.py
import logging
from layer_2_refund.schemas.refund_models import RefundRequest

logger = logging.getLogger("refund_input_adapter")

class RefundInputAdapter:
    @staticmethod
    def build_refund_request(triage_output, unified_ticket) -> RefundRequest:
        """
        Transforms the Triage Output into a structured RefundRequest object.
        Safely extracts data whether the input is a dictionary or a Pydantic model.
        """
        if isinstance(triage_output, dict):
            ticket_id = triage_output.get("ticket_id", "UNKNOWN")
            customer_id = triage_output.get("customer_id", 0)
            entities = triage_output.get("entities", {})
        else:
            ticket_id = getattr(triage_output, "ticket_id", "UNKNOWN")
            customer_id = getattr(triage_output, "customer_id", 0)
            entities = getattr(triage_output, "entities", {})

        raw_order_id = entities.get("order_id", 0) if isinstance(entities, dict) else getattr(entities, "order_id", 0)
        logger.warning(
            "REFUND INPUT BUILD | ticket=%s | customer=%s | entities=%s",
            ticket_id,
            customer_id,
            entities
        )
        if raw_order_id is None:
            raise ValueError(
                "Refund request requires order_id."
            )

        safe_order_id = int(raw_order_id)

        try:
            safe_customer_id = int(customer_id)
        except (ValueError, TypeError):
            safe_customer_id = 0

        return RefundRequest(
            ticket_id=str(ticket_id),
            order_id=safe_order_id,
            customer_id=safe_customer_id,
            reason_for_refund=(
                unified_ticket.get("message_text") or unified_ticket.get("message_raw") or unified_ticket.get("message")
                if isinstance(unified_ticket, dict) else
                getattr(unified_ticket, "message_text", None) or getattr(unified_ticket, "message_raw", None) or getattr(unified_ticket, "message", "No reason provided")
            )
        )