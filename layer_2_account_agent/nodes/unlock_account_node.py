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


def unlock_account(
    state: AccountState,
    auth_provider: AuthProvider,
    idempotency_service: IdempotencyService
) -> Dict[str, Any]:
    """
    Execution node for account unlock workflow.
    """

    ticket_id = state.get("ticket_id")
    customer_id = state.get("resolved_customer_id")
    idempotency_key = state.get("idempotency_key")
    decision = state.get("decision")
    logs = list(state.get("workflow_logs", []))

    if not customer_id or not idempotency_key or not decision:
        logs.append(
            WorkflowLog(
                node="unlock_account_node",
                message="Missing required execution inputs.",
                data={"ticket_id": ticket_id}
            )
        )

        return {
            "workflow_logs": logs,
            "current_node": "unlock_account_node",
            "escalation_required": True,
            "escalation_reason": "Missing execution inputs."
        }

    if not decision.action_allowed:
        logs.append(
            WorkflowLog(
                node="unlock_account_node",
                message="Execution denied by policy.",
                data={"ticket_id": ticket_id}
            )
        )

        return {
            "workflow_logs": logs,
            "current_node": "unlock_account_node",
            "escalation_required": True,
            "escalation_reason": "Action denied."
        }

    if decision.requested_action != ActionType.ACCOUNT_UNLOCK:
        logs.append(
            WorkflowLog(
                node="unlock_account_node",
                message="Incorrect execution route.",
                data={"ticket_id": ticket_id}
            )
        )

        return {
            "workflow_logs": logs,
            "current_node": "unlock_account_node",
            "escalation_required": True,
            "escalation_reason": "Wrong execution route."
        }

    logger.info(
        "Executing unlock_account node ticket_id=%s",
        ticket_id
    )

    try:
        provider_response = auth_provider.unlock_account(
            customer_id=customer_id
        )

        if provider_response.status != ProviderStatus.SUCCESS:
            logger.warning(
                "Unlock provider failed ticket_id=%s",
                ticket_id
            )

            idempotency_service.mark_failed(
                idempotency_key=idempotency_key,
                error_payload=provider_response.model_dump()
            )

            logs.append(
                WorkflowLog(
                    node="unlock_account_node",
                    message="Provider unlock failed.",
                    data={"ticket_id": ticket_id}
                )
            )

            return {
                "provider_response": provider_response,
                "action_result": "Account unlock failed.",
                "workflow_logs": logs,
                "current_node": "unlock_account_node",
                "escalation_required": True,
                "escalation_reason": "Auth provider unlock failed."
            }

        idempotency_service.mark_completed(
            idempotency_key=idempotency_key,
            response_payload=provider_response.model_dump()
        )

        logs.append(
            WorkflowLog(
                node="unlock_account_node",
                message="Account unlock executed successfully.",
                data={
                    "ticket_id": ticket_id,
                    "customer_id": customer_id
                }
            )
        )

        return {
            "provider_response": provider_response,
            "action_result": "Account unlocked successfully.",
            "workflow_logs": logs,
            "current_node": "unlock_account_node"
        }

    except Exception:
        logger.exception(
            "Unlock workflow crashed ticket_id=%s",
            ticket_id
        )

        idempotency_service.mark_failed(
            idempotency_key=idempotency_key,
            error_payload={"system_failure": True}
        )

        logs.append(
            WorkflowLog(
                node="unlock_account_node",
                message="Unlock execution crashed.",
                data={"ticket_id": ticket_id}
            )
        )

        return {
            "workflow_logs": logs,
            "current_node": "unlock_account_node",
            "escalation_required": True,
            "escalation_reason": "Execution failure."
        }