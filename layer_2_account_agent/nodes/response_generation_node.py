import logging
from typing import Dict, Any

from layer_2_account_agent.schemas.account_state import AccountState
from layer_2_account_agent.schemas.domain import ActionType

logger = logging.getLogger(__name__)


def response_generation_node(
    state: AccountState
) -> Dict[str, Any]:
    """
    Final deterministic customer response generator.
    """

    ticket_id = state.get("ticket_id")
    decision = state.get("decision")
    action_result = state.get("action_result")

    security_escalation = state.get("security_escalation")
    escalation_required = state.get("escalation_required")
    clarification_required = state.get("clarification_required")
    clarification_question = state.get("clarification_question")

    logger.info(
        "Executing response_generation node ticket_id=%s",
        ticket_id
    )

    customer_response = (
        "We could not complete your request at this time."
    )


    if clarification_required and clarification_question:
        customer_response = clarification_question


    elif security_escalation:
        customer_response = (
            "For your protection, this request requires manual review. "
            "Our security team will contact you shortly."
        )


    elif decision and not decision.action_allowed:
        customer_response = (
            "We are unable to process this request automatically "
            "based on our security policies. A support agent "
            "has been assigned to assist you."
        )


    elif escalation_required:
        customer_response = (
            "We encountered an issue while processing your request. "
            "Our support team has been notified."
        )


    elif action_result and decision:
        requested_action = decision.requested_action

        if requested_action == ActionType.PASSWORD_RESET:
            customer_response = (
                "We’ve sent a password reset link to your "
                "registered email. Please check your inbox."
            )

        elif requested_action == ActionType.ACCOUNT_UNLOCK:
            customer_response = (
                "Your account has been unlocked successfully. "
                "You can now log in."
            )

        elif requested_action == ActionType.INVOICE_RETRIEVAL:
            customer_response = (
                "Your invoice has been retrieved successfully."
            )

        elif requested_action == ActionType.BILLING_EXPLANATION:
            customer_response = (
                "I retrieved your recent billing activity successfully."
            )

        elif requested_action in [
            ActionType.SUBSCRIPTION_CANCEL,
            ActionType.SUBSCRIPTION_UPGRADE,
            ActionType.SUBSCRIPTION_DOWNGRADE,
            ActionType.SUBSCRIPTION_PAUSE
        ]:
            action_str = (
                requested_action.value
                .replace("_", " ")
                .title()
            )

            customer_response = (
                f"Your {action_str} request has been processed successfully."
            )

        else:
            customer_response = action_result

    logger.info(
        "Response generated successfully ticket_id=%s",
        ticket_id
    )
    logger.warning(
    "FINAL CUSTOMER RESPONSE | ticket=%s | response=%s",
    ticket_id,
    customer_response
)

    return {
        "customer_response": customer_response,
        "current_node": "response_generation_node"
    }