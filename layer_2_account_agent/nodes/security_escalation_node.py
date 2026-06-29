import logging
from typing import Dict, Any, Callable
from datetime import datetime, UTC

from layer_2_account_agent.schemas.account_state import AccountState
from layer_2_account_agent.schemas.domain import (
    WorkflowLog,
    ActionType,
    ProviderResponse,
    ProviderStatus
)
from layer_2_account_agent.services.auth_provider import AuthProvider
from layer_2_account_agent.repositories.security_audit_repository import SecurityAuditRepository
from layer_2_account_agent.services.idempotency_service import IdempotencyService

logger = logging.getLogger(__name__)


def get_security_escalation_node(
    auth_provider: AuthProvider,
    audit_repo: SecurityAuditRepository,
    idempotency_service: IdempotencyService
) -> Callable[[AccountState], Dict[str, Any]]:
    """
    Factory for security escalation node.

    Handles:
    - threat containment
    - manual security review routing
    - immutable audit logging
    - idempotent workflow finalization
    """

    def security_escalation_node(state: AccountState) -> Dict[str, Any]:
        ticket_id = state.get("ticket_id")
        customer_id = state.get("resolved_customer_id")
        takeover_assessment = state.get("takeover_assessment")
        abuse_assessment = state.get("abuse_assessment")
        decision = state.get("decision")
        risk_assessment = state.get("risk_assessment")
        escalation_reason = state.get("escalation_reason")
        idempotency_key = state.get("idempotency_key")

        workflow_id = state.get("workflow_id", "UNKNOWN_WF")
        correlation_id = state.get("correlation_id", "UNKNOWN_CORRELATION")

        logs = list(state.get("workflow_logs", []))

        logger.info(
            "Executing security_escalation_node ticket_id=%s",
            ticket_id
        )

        try:

            require_account_lock = False
            security_reason = escalation_reason or "Security escalation triggered."

            if takeover_assessment and takeover_assessment.takeover_detected:
                require_account_lock = True
                security_reason = (
                    takeover_assessment.reason
                    or "Account takeover risk detected."
                )

            elif abuse_assessment and abuse_assessment.abuse_detected:
                security_reason = (
                    abuse_assessment.reason
                    or "Operational abuse detected."
                )

            elif decision and decision.security_escalation:
                security_reason = (
                    decision.decision_reason
                    or "Security escalation required."
                )


            if require_account_lock and customer_id:
                logger.warning(
                    "Containment triggered customer_id=%s",
                    customer_id
                )

                provider_response = auth_provider.lock_account(
                    customer_id=customer_id,
                    reason=security_reason
                )

                if provider_response.status != ProviderStatus.SUCCESS:
                    raise RuntimeError("Account containment failed.")

            else:
                provider_response = ProviderResponse(
                    provider_name="SecurityEscalation",
                    status=ProviderStatus.SUCCESS,
                    data={
                        "action": "manual_review_routed",
                        "reason": security_reason
                    }
                )


            action_type = (
                decision.requested_action.value
                if decision
                else ActionType.SECURITY_ESCALATION.value
            )

            verification_level = (
                decision.verification_level.value
                if decision and decision.verification_level
                else None
            )

            risk_score = (
                risk_assessment.risk_score
                if risk_assessment
                else 0.0
            )

            audit_logged = audit_repo.log_security_event(
                workflow_id=workflow_id,
                correlation_id=correlation_id,
                action_type=action_type,
                decision="security_escalated",
                customer_id=customer_id,
                ticket_id=ticket_id,
                verification_level=verification_level,
                risk_score=risk_score,
                provider_response=provider_response.model_dump(),
                operator_type="AI"
            )

            if not audit_logged:
                raise RuntimeError("Immutable audit logging failed.")


            if idempotency_key:
                idempotency_service.mark_completed(
                    idempotency_key=idempotency_key,
                    response_payload=provider_response.model_dump()
                )


            logs.append(
                WorkflowLog(
                    node="security_escalation_node",
                    message="Security escalation completed.",
                    timestamp=datetime.now(UTC),
                    data={
                        "ticket_id": ticket_id,
                        "customer_id": customer_id,
                        "account_locked": require_account_lock,
                        "reason": security_reason
                    }
                )
            )


            return {
                "provider_response": provider_response,
                "action_result": (
                    f"Security escalation completed: {security_reason}"
                ),
                "security_escalation": True,
                "workflow_logs": logs,
                "current_node": "security_escalation_node"
            }

        except Exception:
            logger.exception(
                "Security escalation node crashed ticket_id=%s",
                ticket_id
            )

            if idempotency_key:
                idempotency_service.mark_failed(
                    idempotency_key=idempotency_key,
                    error_payload={"system_failure": True}
                )

            logs.append(
                WorkflowLog(
                    node="security_escalation_node",
                    message="Security escalation execution failed.",
                    timestamp=datetime.now(UTC),
                    data={"ticket_id": ticket_id}
                )
            )

            return {
                "escalation_required": True,
                "escalation_reason": "Security escalation execution failed.",
                "workflow_logs": logs,
                "current_node": "security_escalation_node"
            }

    return security_escalation_node