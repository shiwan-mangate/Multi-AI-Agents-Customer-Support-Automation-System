
import logging
from typing import Dict, Any

from layer_2_account_agent.schemas.account_state import AccountState
from layer_2_account_agent.schemas.domain import WorkflowLog
from layer_2_account_agent.repositories.account_repository import AccountRepository
from layer_2_account_agent.repositories.billing_repository import BillingRepository

logger = logging.getLogger(__name__)


def fetch_account_context(
    state: AccountState,
    account_repo: AccountRepository,
    billing_repo: BillingRepository
) -> Dict[str, Any]:
    """
    Node 5: Account context hydration.

    Loads account operational context from PostgreSQL.
    """

    resolved_customer_id = state.get("resolved_customer_id")
    ticket_id = state.get("ticket_id")
    logs = list(state.get("workflow_logs", []))

    logger.info(
        "Executing fetch_account_context node ticket_id=%s",
        ticket_id
    )


    if not resolved_customer_id:
        logs.append(
            WorkflowLog(
                node="fetch_account_context_node",
                message="No resolved customer identity. Empty context fallback applied.",
                data={
                    "ticket_id": ticket_id
                }
            )
        )

        return {
            "auth_context": {},
            "subscription_context": {},
            "billing_context": [],
            "workflow_logs": logs,
            "current_node": "fetch_account_context_node"
        }

    try:
        auth_context = (
            account_repo.get_auth_account(resolved_customer_id)
            or {}
        )

        subscription_context = (
            account_repo.get_subscription(resolved_customer_id)
            or {}
        )

        billing_context = (
            billing_repo.get_billing_history(resolved_customer_id)
            or []
        )

        logs.append(
            WorkflowLog(
                node="fetch_account_context_node",
                message="Account context hydrated successfully.",
                data={
                    "ticket_id": ticket_id,
                    "customer_id": resolved_customer_id,
                    "auth_found": bool(auth_context),
                    "subscription_found": bool(subscription_context),
                    "billing_records": len(billing_context)
                }
            )
        )

        return {
            "auth_context": auth_context,
            "subscription_context": subscription_context,
            "billing_context": billing_context,
            "workflow_logs": logs,
            "current_node": "fetch_account_context_node"
        }

    except Exception:
        logger.exception(
            "Account context hydration failed ticket_id=%s",
            ticket_id
        )

        logs.append(
            WorkflowLog(
                node="fetch_account_context_node",
                message="Account context hydration failed. Empty fallback applied.",
                data={
                    "ticket_id": ticket_id
                }
            )
        )

        return {
            "auth_context": {},
            "subscription_context": {},
            "billing_context": [],
            "workflow_logs": logs,
            "current_node": "fetch_account_context_node"
        }