import logging
from typing import Dict, Any

from layer_2_account_agent.schemas.account_state import AccountState
from layer_2_account_agent.schemas.domain import WorkflowLog
from layer_2_account_agent.repositories.security_audit_repository import SecurityAuditRepository

logger = logging.getLogger(__name__)


def audit_log(
    state: AccountState,
    audit_repo: SecurityAuditRepository
) -> Dict[str, Any]:
    """
    Node: Immutable audit logging.

    Records ALL workflow outcomes:
    - approved execution
    - denied by policy
    - security escalation
    - failed execution
    - duplicate cached replay

    Compliance logging must happen even when execution never occurs.
    """

    ticket_id = state.get("ticket_id")
    customer_id = state.get("resolved_customer_id")
    decision = state.get("decision")
    provider_response = state.get("provider_response")
    risk_assessment = state.get("risk_assessment")

    logs = list(state.get("workflow_logs", []))

    logger.info(
        "Executing audit_log node ticket_id=%s",
        ticket_id
    )


    if not decision:
        logs.append(
            WorkflowLog(
                node="audit_log_node",
                message="Missing decision. Cannot perform audit log.",
                data={"ticket_id": ticket_id}
            )
        )

        return {
            "workflow_logs": logs,
            "current_node": "audit_log_node",
            "escalation_required": True,
            "escalation_reason": "Missing audit inputs (decision)."
        }

    # ---------------------------------------------------------
    # Optional provider payload
    # ---------------------------------------------------------
    provider_payload = {}

    if provider_response:
        provider_payload = (
            provider_response.model_dump()
            if hasattr(provider_response, "model_dump")
            else provider_response
        )

    # ---------------------------------------------------------
    # Audit decision classification
    # ORDER MATTERS
    # ---------------------------------------------------------
    if state.get("duplicate_cached_response"):
        final_decision_text = "duplicate_cached_response"

    elif state.get("security_escalation"):
        final_decision_text = "security_escalated"

    elif not decision.action_allowed:
        final_decision_text = "denied_by_policy"

    elif state.get("escalation_required"):
        final_decision_text = "execution_failed"

    else:
        final_decision_text = "approved_and_executed"

    try:
        action_type = decision.requested_action.value
        verification_level = decision.verification_level.value

        risk_score = (
            risk_assessment.risk_score
            if risk_assessment
            else 0.0
        )

        audit_logged = audit_repo.log_security_event(
            workflow_id=state.get(
                "workflow_id",
                "UNKNOWN_WF"
            ),
            correlation_id=state.get(
                "correlation_id",
                "UNKNOWN_CORRELATION"
            ),
            action_type=action_type,
            decision=final_decision_text,
            customer_id=customer_id,
            ticket_id=ticket_id,
            verification_level=verification_level,
            risk_score=risk_score,
            provider_response=provider_payload,
            operator_type="AI"
        )

        if not audit_logged:
            logs.append(
                WorkflowLog(
                    node="audit_log_node",
                    message="Audit logging failed.",
                    data={"ticket_id": ticket_id}
                )
            )

            return {
                "workflow_logs": logs,
                "current_node": "audit_log_node",
                "escalation_required": True,
                "escalation_reason": "Audit logging failed."
            }

        logs.append(
            WorkflowLog(
                node="audit_log_node",
                message=(
                    f"Audit logging successful "
                    f"decision={final_decision_text}"
                ),
                data={
                    "ticket_id": ticket_id,
                    "action": action_type
                }
            )
        )

        return {
            "audit_logged": True,
            "workflow_logs": logs,
            "current_node": "audit_log_node"
        }

    except Exception:
        logger.exception(
            "Audit log node crashed ticket_id=%s",
            ticket_id
        )

        logs.append(
            WorkflowLog(
                node="audit_log_node",
                message="Audit log execution crashed.",
                data={"ticket_id": ticket_id}
            )
        )

        return {
            "workflow_logs": logs,
            "current_node": "audit_log_node",
            "escalation_required": True,
            "escalation_reason": "Audit execution failure."
        }