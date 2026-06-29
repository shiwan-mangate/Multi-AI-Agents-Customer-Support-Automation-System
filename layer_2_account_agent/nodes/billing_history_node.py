from layer_2_account_agent.schemas.account_state import AccountState
from layer_2_account_agent.schemas.domain import (
    WorkflowLog,
    ActionType,
    ProviderResponse,
    ProviderStatus
)
from layer_2_account_agent.repositories.billing_repository import BillingRepository
from layer_2_account_agent.services.idempotency_service import IdempotencyService
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)


def billing_history(
    state: AccountState,
    billing_repo: BillingRepository,
    idempotency_service: IdempotencyService
) -> Dict[str, Any]:
    """
    Execution node for billing history explanation.
    """

    ticket_id = state.get("ticket_id")
    customer_id = state.get("resolved_customer_id")
    decision = state.get("decision")
    idempotency_key = state.get("idempotency_key")
    logs = list(state.get("workflow_logs", []))

    if not customer_id or not idempotency_key or not decision:
        logs.append(
            WorkflowLog(
                node="billing_history_node",
                message="Missing required execution inputs.",
                data={"ticket_id": ticket_id}
            )
        )

        return {
            "workflow_logs": logs,
            "current_node": "billing_history_node",
            "escalation_required": True,
            "escalation_reason": "Missing execution inputs."
        }

    if not decision.action_allowed:
        idempotency_service.mark_failed(
            idempotency_key=idempotency_key,
            error_payload={"reason": "action_denied"}
        )

        logs.append(
            WorkflowLog(
                node="billing_history_node",
                message="Execution denied by policy.",
                data={"ticket_id": ticket_id}
            )
        )

        return {
            "workflow_logs": logs,
            "current_node": "billing_history_node",
            "escalation_required": True,
            "escalation_reason": "Action denied."
        }

    if decision.requested_action != ActionType.BILLING_EXPLANATION:
        idempotency_service.mark_failed(
            idempotency_key=idempotency_key,
            error_payload={"reason": "wrong_route"}
        )

        logs.append(
            WorkflowLog(
                node="billing_history_node",
                message="Incorrect execution route.",
                data={"ticket_id": ticket_id}
            )
        )

        return {
            "workflow_logs": logs,
            "current_node": "billing_history_node",
            "escalation_required": True,
            "escalation_reason": "Wrong execution route."
        }

    logger.info(
        "Executing billing_history node ticket_id=%s",
        ticket_id
    )

    try:
        billing_history = billing_repo.get_billing_history(
            customer_id=customer_id,
            limit=5
        )

        failed_payments = billing_repo.get_failed_payments(
            customer_id=customer_id,
            limit=5
        )

        provider_response = ProviderResponse(
            provider_name="InternalBilling",
            status=ProviderStatus.SUCCESS,
            data={
                "billing_history": billing_history,
                "failed_payments": failed_payments
            }
        )

        idempotency_service.mark_completed(
            idempotency_key=idempotency_key,
            response_payload=provider_response.model_dump()
        )

        logs.append(
            WorkflowLog(
                node="billing_history_node",
                message="Billing history retrieved successfully.",
                data={
                    "ticket_id": ticket_id,
                    "customer_id": customer_id
                }
            )
        )

        return {
            "provider_response": provider_response,
            "action_result": "Billing history retrieved successfully.",
            "workflow_logs": logs,
            "current_node": "billing_history_node"
        }

    except Exception:
        logger.exception(
            "Billing history retrieval workflow crashed ticket_id=%s",
            ticket_id
        )

        idempotency_service.mark_failed(
            idempotency_key=idempotency_key,
            error_payload={"system_failure": True}
        )

        logs.append(
            WorkflowLog(
                node="billing_history_node",
                message="Billing history retrieval execution crashed.",
                data={"ticket_id": ticket_id}
            )
        )

        return {
            "workflow_logs": logs,
            "current_node": "billing_history_node",
            "escalation_required": True,
            "escalation_reason": "Execution failure."
        }