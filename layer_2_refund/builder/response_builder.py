# layer_2_refund/builders/response_builder.py

from typing import Any
from layer_2_refund.schemas.refund_models import (
    PolicyDecision,
    RefundExecutionResult,
)


def _safe_float(val: Any, default: float = 0.0) -> float:
    """Safely extracts and casts a float from unstructured metadata."""
    try:
        return float(val) if val is not None else default
    except (ValueError, TypeError):
        return default


def build_customer_response(
    decision: PolicyDecision,
    order_id: int,
    execution_result: RefundExecutionResult | None = None
) -> str:
    """
    Translates internal system decisions and states into highly empathetic,
    professional, and safe customer-facing communications.
    """
    
    code = decision.code
    metadata = decision.metadata or {}


    if code == "REFUND_EXECUTED":
        txn_id = execution_result.transaction_id if execution_result else "N/A"
        refund_amount = _safe_float(
            decision.refund_amount or metadata.get("refund_amount")
        )

        return (
            f"Your refund request for order {order_id} "
            f"has been approved and successfully processed. "
            f"A refund of ${refund_amount:.2f} has been issued. "
            f"Transaction ID: {txn_id}. "
            f"The funds should appear in your original payment "
            f"method within 5–7 business days."
        )

    if code == "POLICY_APPROVED":
        
        return (
            f"Your refund request for order {order_id} "
            f"has been approved and is currently being processed."
        )

    if code == "HUMAN_APPROVED":
        refund_amount = _safe_float(metadata.get("refund_amount"))

        return (
            f"Your refund request for order {order_id} "
            f"has been reviewed and approved by our support team. "
            f"A refund of ${refund_amount:.2f} will now be processed."
        )



    if code == "HIGH_VALUE_REVIEW":
        order_amount = _safe_float(metadata.get("order_amount"))
        threshold = _safe_float(metadata.get("threshold", 500.0))

        return (
            f"Your refund request for order {order_id} "
            f"has been received and requires manual review. "
            f"The requested refund amount of "
            f"${order_amount:.2f} exceeds the automatic "
            f"approval threshold of ${threshold:.2f}. "
            f"Our support team will review the request within "
            f"24 hours and provide an update."
        )

    if code == "FRAUD_RISK_DETECTED":
        
        return (
            f"Your refund request for order {order_id} "
            f"requires additional verification before a final "
            f"decision can be made. "
            f"Our support team will manually review the request "
            f"and contact you if further information is needed. "
            f"No action is required from you at this time."
        )


    if code == "OUTSIDE_WINDOW":
        days_since = metadata.get("days_since_purchase")
        allowed = metadata.get("allowed_window")

        if days_since is not None and allowed is not None:
            return (
                f"We reviewed your refund request for order {order_id}. "
                f"Our records show that the order was placed "
                f"{days_since} days ago. "
                f"The refund eligibility window for this order is "
                f"{allowed} days. "
                f"Because the request falls outside the eligible "
                f"refund period, we are unable to approve the refund."
            )
        return (
            f"We reviewed your refund request for order {order_id}. "
            f"Unfortunately, the request falls outside the eligible "
            f"refund period and cannot be approved."
        )

    if code == "NOT_DELIVERED":
        raw_status = metadata.get("current_order_status", "UNKNOWN")
        status_display = str(raw_status).replace("_", " ").title()

        return (
            f"We reviewed your refund request for order {order_id}. "
            f"Our records show that the order is currently "
            f"'{status_display}'. "
            f"Refunds can only be processed after delivery "
            f"has been confirmed."
        )

    if code == "NOT_REFUNDABLE":
        return (
            f"We reviewed your refund request for order {order_id}. "
            f"This item is classified as non-refundable "
            f"under our refund policy and is therefore "
            f"not eligible for a refund."
        )

    if code == "HUMAN_REJECTED":
        return (
            f"We reviewed your refund request for order {order_id}. "
            f"After manual review, we are unable to approve "
            f"the refund at this time."
        )



    if code == "INVALID_DATE":
        return (
            f"We were unable to process your refund request for order {order_id} "
            f"due to a date discrepancy in our system. "
            f"Our support team has been notified and will investigate."
        )

    
    return (
        f"We reviewed your refund request for order {order_id}. "
        f"{decision.reason}"
    )