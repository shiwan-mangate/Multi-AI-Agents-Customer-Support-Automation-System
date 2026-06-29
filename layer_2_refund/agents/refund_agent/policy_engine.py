from layer_2_refund.schemas.refund_models import (
    CustomerData, OrderData, OrderStatus, 
    PolicyDecision, RefundStatus
)
from datetime import datetime, timedelta

# Configuration Constants
VIP_TIERS = {"enterprise", "premium"} 
STANDARD_REFUND_WINDOW = 30
VIP_REFUND_WINDOW = 60
HIGH_VALUE_THRESHOLD = 500.00
NEW_ACCOUNT_THRESHOLD_DAYS = 90

def _get_account_age_days(
    customer: CustomerData,
    now: datetime
) -> int:
    """Calculates the age of the customer account in days."""
    return (now - customer.created_at).days

def _is_fraud_risk_detected(
    order: OrderData,
    account_age_days: int
) -> bool:
    """
    Refined Fraud Logic:
    - Detects suspicious high-value activity
      from very new accounts
    """
    is_new_account = (
        account_age_days
        <= NEW_ACCOUNT_THRESHOLD_DAYS
    )

    if is_new_account and order.order_amount > 100.00:
        return True

    return False

def evaluate_refund(order: OrderData, customer: CustomerData) -> PolicyDecision:
    now = datetime.now(order.created_at.tzinfo) 
    
    account_age_days = _get_account_age_days(customer, now)

   
    if order.created_at > now:
        return PolicyDecision(
            status=RefundStatus.REJECTED,
            code="INVALID_DATE",
            reason="Purchase date is in the future. Data corruption suspected.",
            metadata={
                "purchase_date": order.created_at.isoformat(),
                "evaluation_time": now.isoformat()
            }
        )

  
    if order.is_refundable is False:
        return PolicyDecision(
            status=RefundStatus.REJECTED,
            code="NOT_REFUNDABLE",
            reason="This specific item/order is non-refundable.",
            metadata={
                "refund_policy_type": "NON_REFUNDABLE_ITEM"
            }
        )

   
    if _is_fraud_risk_detected(order, account_age_days):
        return PolicyDecision(
            status=RefundStatus.ESCALATED,
            requires_human_review=True,
            code="FRAUD_RISK_DETECTED",
            reason="Automated risk flags triggered based on account history/behavior.",
            metadata={
                "account_age_days": account_age_days,
                "order_amount": order.order_amount
            }
        )

  
    if order.order_status != OrderStatus.DELIVERED:
        return PolicyDecision(
            status=RefundStatus.REJECTED,
            code="NOT_DELIVERED",
            reason="Refunds cannot be processed until delivery is confirmed.",
            metadata={
                "current_order_status": order.order_status.value
            }
        )

    
    if order.order_amount > HIGH_VALUE_THRESHOLD:
        return PolicyDecision(
            status=RefundStatus.ESCALATED,
            requires_human_review=True,
            code="HIGH_VALUE_REVIEW",
            reason=f"Refund exceeds {HIGH_VALUE_THRESHOLD}. Standard audit required.",
            metadata={
                "priority": (
                    "urgent"
                    if customer.account_tier in VIP_TIERS
                    else "high"
                ),
                "order_amount": order.order_amount,
                "threshold": HIGH_VALUE_THRESHOLD
            }
        )

   
    days_since_purchase = (now - order.created_at).days
    allowed_window = VIP_REFUND_WINDOW if customer.account_tier in VIP_TIERS else STANDARD_REFUND_WINDOW
    
    if days_since_purchase > allowed_window:
        return PolicyDecision(
            status=RefundStatus.REJECTED,
            code="OUTSIDE_WINDOW",
            reason=f"Refund period of {allowed_window} days has expired.",
            metadata={
                "days_since_purchase": days_since_purchase,
                "allowed_window": allowed_window,
                "account_tier": customer.account_tier
            }
        )


    return PolicyDecision(
        status=RefundStatus.APPROVED,
        code="POLICY_APPROVED",
        reason="Criteria met. Auto-approval granted.",
        refund_amount=order.order_amount,
        metadata={
            "refund_amount": order.order_amount
        }
    )