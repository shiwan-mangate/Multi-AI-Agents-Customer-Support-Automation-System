

import logging
from typing import Dict, Any

from layer_2_account_agent.schemas.account_state import AccountState
from layer_2_account_agent.schemas.domain import (
    WorkflowLog,
    ActionType,
    ProviderStatus
)
from layer_2_account_agent.services.auth_provider import AuthProvider
from layer_2_account_agent.services.idempotency_service import IdempotencyService

logger = logging.getLogger(__name__)


def password_reset(
    state: AccountState,
    auth_provider: AuthProvider,
    idempotency_service: IdempotencyService
) -> Dict[str, Any]:
    """
    Execution node for password reset workflow.
    """

    ticket_id = state.get("ticket_id")
    customer_email = state.get("customer_email")
    customer_id = state.get("resolved_customer_id")
    decision = state.get("decision")
    idempotency_key = state.get("idempotency_key")

    logs = list(state.get("workflow_logs", []))

    logger.info(
        "Executing password_reset node ticket_id=%s",
        ticket_id
    )


    if not customer_email or not customer_id or not idempotency_key:
        logs.append(
            WorkflowLog(
                node="password_reset_node",
                message="Missing required execution inputs.",
                data={"ticket_id": ticket_id}
            )
        )

        return {
            "workflow_logs": logs,
            "current_node": "password_reset_node",
            "escalation_required": True,
            "escalation_reason": "Missing execution inputs."
        }

    if not decision:
        logs.append(
            WorkflowLog(
                node="password_reset_node",
                message="Missing decision context.",
                data={"ticket_id": ticket_id}
            )
        )

        return {
            "workflow_logs": logs,
            "current_node": "password_reset_node",
            "escalation_required": True,
            "escalation_reason": "Missing decision."
        }

    if not decision.action_allowed:
        logs.append(
            WorkflowLog(
                node="password_reset_node",
                message="Execution denied by policy.",
                data={"ticket_id": ticket_id}
            )
        )

        return {
            "workflow_logs": logs,
            "current_node": "password_reset_node",
            "escalation_required": True,
            "escalation_reason": "Action denied."
        }

    if decision.requested_action != ActionType.PASSWORD_RESET:
        logs.append(
            WorkflowLog(
                node="password_reset_node",
                message="Incorrect execution route.",
                data={"ticket_id": ticket_id}
            )
        )

        return {
            "workflow_logs": logs,
            "current_node": "password_reset_node",
            "escalation_required": True,
            "escalation_reason": "Wrong execution route."
        }


    try:
        provider_response = auth_provider.reset_password(
            customer_id=customer_id,
            email=customer_email
        )

        # Provider failed
        if provider_response.status != ProviderStatus.SUCCESS:
            idempotency_service.mark_failed(
                idempotency_key=idempotency_key,
                error_payload=provider_response.model_dump()
            )

            logs.append(
                WorkflowLog(
                    node="password_reset_node",
                    message="Provider password reset failed.",
                    data={"ticket_id": ticket_id}
                )
            )

            return {
                "provider_response": provider_response,
                "action_result": "Password reset failed.",
                "workflow_logs": logs,
                "current_node": "password_reset_node",
                "escalation_required": True,
                "escalation_reason": "Auth provider failed."
            }

        # Success
        idempotency_service.mark_completed(
            idempotency_key=idempotency_key,
            response_payload=provider_response.model_dump()
        )

        logs.append(
            WorkflowLog(
                node="password_reset_node",
                message="Password reset executed successfully.",
                data={
                    "ticket_id": ticket_id,
                    "customer_id": customer_id
                }
            )
        )

        return {
            "provider_response": provider_response,
            "action_result": "Password reset email sent successfully.",
            "workflow_logs": logs,
            "current_node": "password_reset_node"
        }

    except Exception:
        logger.exception(
            "Password reset workflow failed ticket_id=%s",
            ticket_id
        )

        idempotency_service.mark_failed(
            idempotency_key=idempotency_key,
            error_payload={"system_failure": True}
        )

        logs.append(
            WorkflowLog(
                node="password_reset_node",
                message="Password reset execution crashed.",
                data={"ticket_id": ticket_id}
            )
        )

        return {
            "workflow_logs": logs,
            "current_node": "password_reset_node",
            "escalation_required": True,
            "escalation_reason": "Execution failure."
        }