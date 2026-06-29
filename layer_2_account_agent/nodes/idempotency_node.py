import logging
from typing import Dict, Any

from layer_2_account_agent.schemas.account_state import AccountState
from layer_2_account_agent.schemas.domain import WorkflowLog
from layer_2_account_agent.services.idempotency_service import IdempotencyService

logger = logging.getLogger(__name__)


def idempotency(
    state: AccountState,
    idempotency_service: IdempotencyService
) -> Dict[str, Any]:
    """
    Node: Idempotent execution gate.
    Prevents duplicate workflow execution.
    """

    ticket_id = state.get("ticket_id")
    decision = state.get("decision")
    resolved_customer_id = state.get("resolved_customer_id")

    logs = list(state.get("workflow_logs", []))

    logger.info(
        "Executing idempotency node ticket_id=%s",
        ticket_id
    )

    # ---------------------------------------------------------
    # Missing required inputs
    # ---------------------------------------------------------
    if not decision or not resolved_customer_id:
        logs.append(
            WorkflowLog(
                node="idempotency_node",
                message="Missing decision or customer identity. Fail closed.",
                data={"ticket_id": ticket_id}
            )
        )

        return {
            "idempotency_blocked": True,
            "duplicate_cached_response": False,
            "skip_execution": True,
            "action_result": "Execution blocked due to missing identity/decision.",
            "workflow_logs": logs,
            "current_node": "idempotency_node",
            "escalation_required": True,
            "escalation_reason": "Missing decision or customer identity."
        }

    # ---------------------------------------------------------
    # Policy denied
    # ---------------------------------------------------------
    if not decision.action_allowed:
        logs.append(
            WorkflowLog(
                node="idempotency_node",
                message="Action denied by policy. Execution skipped.",
                data={"ticket_id": ticket_id}
            )
        )

        return {
            "idempotency_blocked": True,
            "duplicate_cached_response": False,
            "skip_execution": True,
            "action_result": "Action denied by policy.",
            "workflow_logs": logs,
            "current_node": "idempotency_node"
        }

    requested_action = decision.requested_action
    idempotency_key = f"{resolved_customer_id}:{requested_action.value}"

    try:
        reserved = idempotency_service.reserve_execution(
            idempotency_key=idempotency_key,
            action_type=requested_action,
            customer_id=resolved_customer_id
        )

        if not reserved:
            cached_response = idempotency_service.get_cached_result(
                idempotency_key
            )

            # DUPLICATE COMPLETED REQUEST
            if cached_response:
                logger.warning(
                        "IDEMPOTENCY CACHE HIT | key=%s | cached=%s",
                        idempotency_key,
                        cached_response
                    )
                logs.append(
                    WorkflowLog(
                        node="idempotency_node",
                        message="Duplicate completed request detected. Cached response reused.",
                        data={"ticket_id": ticket_id}
                    )
                )

                return {
                    "idempotency_blocked": True,
                    "duplicate_cached_response": True,
                    "provider_response": cached_response,
                    "action_result": "Duplicate request ignored. Cached result reused.",
                    "workflow_logs": logs,
                    "current_node": "idempotency_node"
                }

            # DUPLICATE IN PROGRESS
            logs.append(
                WorkflowLog(
                    node="idempotency_node",
                    message="Duplicate in-progress request blocked.",
                    data={"ticket_id": ticket_id}
                )
            )

            return {
                "idempotency_blocked": True,
                "duplicate_cached_response": False,
                "escalation_required": True,
                "escalation_reason": "Duplicate in-progress request blocked.",
                "workflow_logs": logs,
                "current_node": "idempotency_node"
            }

        # FRESH EXECUTION
        logs.append(
            WorkflowLog(
                node="idempotency_node",
                message="Execution slot reserved successfully.",
                data={
                    "ticket_id": ticket_id,
                    "idempotency_key": idempotency_key
                }
            )
        )

        return {
            "idempotency_key": idempotency_key,
            "idempotency_blocked": False,
            "duplicate_cached_response": False,
            "skip_execution": False,
            "workflow_logs": logs,
            "current_node": "idempotency_node"
        }

    except Exception:
        logger.exception(
            "Idempotency node failed ticket_id=%s",
            ticket_id
        )

        logs.append(
            WorkflowLog(
                node="idempotency_node",
                message="Idempotency failure. Execution blocked.",
                data={"ticket_id": ticket_id}
            )
        )
    

        return {
            "idempotency_blocked": True,
            "duplicate_cached_response": False,
            "skip_execution": True,
            "action_result": "Execution blocked due to idempotency failure.",
            "workflow_logs": logs,
            "current_node": "idempotency_node",
            "escalation_required": True,
            "escalation_reason": "Idempotency failure."
        }