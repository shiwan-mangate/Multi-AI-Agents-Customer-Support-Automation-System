import logging
from typing import Dict, Any

from layer_2_account_agent.schemas.account_state import AccountState
from layer_2_account_agent.schemas.domain import (
    WorkflowLog,
    ActionType,
    ProviderResponse,
    ProviderStatus
)
from layer_2_account_agent.repositories.billing_repository import BillingRepository
from layer_2_account_agent.services.idempotency_service import IdempotencyService

logger = logging.getLogger(__name__)


def invoice_retrieval(
    state: AccountState,
    billing_repo: BillingRepository,
    idempotency_service: IdempotencyService
) -> Dict[str, Any]:
    """
    Execution node for billing invoice retrieval.
    """

    ticket_id = state.get("ticket_id")
    customer_id = state.get("resolved_customer_id")
    decision = state.get("decision")
    entities = state.get("entities", {})
    idempotency_key = state.get("idempotency_key")
    logs = list(state.get("workflow_logs", []))

    if not customer_id or not idempotency_key or not decision:
        logs.append(
            WorkflowLog(
                node="invoice_retrieval_node",
                message="Missing required execution inputs.",
                data={"ticket_id": ticket_id}
            )
        )

        return {
            "workflow_logs": logs,
            "current_node": "invoice_retrieval_node",
            "escalation_required": True,
            "escalation_reason": "Missing execution inputs."
        }
    logger.warning(
    "INVOICE INPUT | customer=%s | order_id=%s",
    customer_id,
    entities.get("order_id")
)

    if not decision.action_allowed:
        logs.append(
            WorkflowLog(
                node="invoice_retrieval_node",
                message="Execution denied by policy.",
                data={"ticket_id": ticket_id}
            )
        )

        return {
            "workflow_logs": logs,
            "current_node": "invoice_retrieval_node",
            "escalation_required": True,
            "escalation_reason": "Action denied."
        }

    if decision.requested_action != ActionType.INVOICE_RETRIEVAL:
        logs.append(
            WorkflowLog(
                node="invoice_retrieval_node",
                message="Incorrect execution route.",
                data={"ticket_id": ticket_id}
            )
        )

        return {
            "workflow_logs": logs,
            "current_node": "invoice_retrieval_node",
            "escalation_required": True,
            "escalation_reason": "Wrong execution route."
        }

    logger.info(
        "Executing invoice_retrieval node ticket_id=%s",
        ticket_id
    )

    try:
        invoice_id = entities.get("invoice_id")

        if invoice_id:
            invoice = billing_repo.get_invoice_by_id(invoice_id)
        else:
            invoices = billing_repo.get_billing_history(
                customer_id=customer_id,
                limit=1
            )
            logger.warning(
            "BILLING HISTORY RESULT | customer=%s | invoices=%s",
            customer_id,
            invoices
        )
            invoice = invoices[0] if invoices else None

        if not invoice:
            idempotency_service.mark_failed(
                idempotency_key=idempotency_key,
                error_payload={"reason": "invoice_not_found"}
            )

            logs.append(
                WorkflowLog(
                    node="invoice_retrieval_node",
                    message="No invoice found.",
                    data={"ticket_id": ticket_id}
                )
            )

            return {
                "workflow_logs": logs,
                "current_node": "invoice_retrieval_node",
                "escalation_required": True,
                "escalation_reason": "Invoice not found."
            }

        # SECURITY OWNERSHIP CHECK
        if invoice["customer_id"] != customer_id:
            idempotency_service.mark_failed(
                idempotency_key=idempotency_key,
                error_payload={"security_violation": True}
            )

            logs.append(
                WorkflowLog(
                    node="invoice_retrieval_node",
                    message="Invoice ownership mismatch detected.",
                    data={"ticket_id": ticket_id}
                )
            )

            return {
                "workflow_logs": logs,
                "current_node": "invoice_retrieval_node",
                "escalation_required": True,
                "security_escalation": True,
                "escalation_reason": "Invoice ownership mismatch."
            }

        provider_response = ProviderResponse(
            provider_name="InternalBilling",
            status=ProviderStatus.SUCCESS,
            data={"invoice": invoice}
        )

        idempotency_service.mark_completed(
            idempotency_key=idempotency_key,
            response_payload=invoice
        )

        logs.append(
            WorkflowLog(
                node="invoice_retrieval_node",
                message="Invoice retrieved successfully.",
                data={
                    "ticket_id": ticket_id,
                    "customer_id": customer_id
                }
            )
        )

        return {
            "provider_response": provider_response,
            "action_result": "Invoice retrieved successfully.",
            "workflow_logs": logs,
            "current_node": "invoice_retrieval_node"
        }

    except Exception:
        logger.exception(
            "Invoice retrieval workflow crashed ticket_id=%s",
            ticket_id
        )

        idempotency_service.mark_failed(
            idempotency_key=idempotency_key,
            error_payload={"system_failure": True}
        )

        logs.append(
            WorkflowLog(
                node="invoice_retrieval_node",
                message="Invoice retrieval execution crashed.",
                data={"ticket_id": ticket_id}
            )
        )

        return {
            "workflow_logs": logs,
            "current_node": "invoice_retrieval_node",
            "escalation_required": True,
            "escalation_reason": "Execution failure."
        }