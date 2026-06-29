from layer_2_account_agent.schemas.account_state import AccountState
from layer_2_account_agent.schemas.domain import (
    WorkflowLog,
    AccountDecision,
    VerificationLevel,
    RiskLevel,
    ActionType
)
import logging
from typing import Dict, Any
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


def verification_policy(
    state: AccountState
) -> Dict[str, Any]:
    """
    Final policy decision engine.

    Security model:
    - Dangerous actions require strict identity verification
    - Read-only actions allow moderate-confidence access
    """

    ticket_id = state.get("ticket_id")
    requested_action = state.get("requested_action")
    verification_level = state.get(
        "verification_level",
        VerificationLevel.FAILED
    )
    risk_assessment = state.get("risk_assessment")

    resolved_customer_id = state.get("resolved_customer_id")
    identity_confidence = state.get("identity_confidence", 0.0)

    logs = list(state.get("workflow_logs", []))

    logger.info(
        "Executing verification_policy node ticket_id=%s",
        ticket_id
    )

    if not requested_action or not risk_assessment:
        logger.warning(
    "POLICY DECISION | ticket=%s | action=%s | allowed=%s | escalation=%s | reason=%s",
    ticket_id,
    decision.requested_action,
    decision.action_allowed,
    decision.security_escalation,
    decision.decision_reason
)
        return {
            "escalation_required": True,
            "escalation_reason": "Missing policy inputs.",
            "current_node": "verification_policy_node"
        }

    risk_level = risk_assessment.risk_level

    # ---------------------------------------------------------
    # SECURITY ESCALATION POLICY
    # ---------------------------------------------------------
    if requested_action == ActionType.SECURITY_ESCALATION:

        decision = AccountDecision(
            requested_action=requested_action,
            verification_level=verification_level,
            risk_level=risk_level,
            action_allowed=False,
            decision_reason="Security review required",
            escalation_required=True,
            security_escalation=True
        )

        logs.append(
            WorkflowLog(
                node="verification_policy_node",
                message="Security escalation triggered",
                timestamp=datetime.now(timezone.utc),
                data={
                    "ticket_id": ticket_id,
                    "action": requested_action.value
                }
            )
        )
        logger.warning(
    "POLICY DECISION | ticket=%s | action=%s | allowed=%s | escalation=%s | reason=%s",
    ticket_id,
    decision.requested_action,
    decision.action_allowed,
    decision.security_escalation,
    decision.decision_reason
)

        return {
            "decision": decision,
            "workflow_logs": logs,
            "current_node": "verification_policy_node"
        }

    # ---------------------------------------------------------
    # READ-ONLY RELAXED POLICY
    # ---------------------------------------------------------
    read_only_actions = {
        ActionType.BILLING_EXPLANATION,
        ActionType.INVOICE_RETRIEVAL
    }

    if (
        requested_action in read_only_actions
        and resolved_customer_id
        and identity_confidence >= 40
        and risk_level != RiskLevel.HIGH
    ):
        decision = AccountDecision(
            requested_action=requested_action,
            verification_level=verification_level,
            risk_level=risk_level,
            action_allowed=True,
            decision_reason=(
                "Read-only action allowed with moderate confidence"
            ),
            escalation_required=False,
            security_escalation=False
        )
        logger.warning(
    "POLICY INPUT | ticket=%s | action=%s | verification=%s | confidence=%s | customer=%s | risk=%s",
    ticket_id,
    requested_action,
    verification_level,
    identity_confidence,
    resolved_customer_id,
    risk_level
)

        logs.append(
            WorkflowLog(
                node="verification_policy_node",
                message=(
                    "Read-only policy approval "
                    f"allowed={decision.action_allowed}"
                ),
                timestamp=datetime.now(timezone.utc),
                data={
                    "ticket_id": ticket_id,
                    "action": requested_action.value
                }
            )
        )
        logger.warning(
    "POLICY DECISION | ticket=%s | action=%s | allowed=%s | escalation=%s | reason=%s",
    ticket_id,
    decision.requested_action,
    decision.action_allowed,
    decision.security_escalation,
    decision.decision_reason
)

        return {
            "decision": decision,
            "workflow_logs": logs,
            "current_node": "verification_policy_node"
        }

    # ---------------------------------------------------------
    # STRICT POLICY FOR DANGEROUS ACTIONS
    # ---------------------------------------------------------
    action_allowed = (
        verification_level != VerificationLevel.FAILED
        and risk_level != RiskLevel.HIGH
    )

    decision = AccountDecision(
        requested_action=requested_action,
        verification_level=verification_level,
        risk_level=risk_level,
        action_allowed=action_allowed,
        decision_reason=(
            "Approved"
            if action_allowed
            else "Denied by security policy"
        ),
        escalation_required=not action_allowed,
        security_escalation=(risk_level == RiskLevel.HIGH)
    )

    logs.append(
        WorkflowLog(
            node="verification_policy_node",
            message=(
                f"Policy decision "
                f"allowed={decision.action_allowed}"
            ),
            timestamp=datetime.now(timezone.utc),
            data={
                "ticket_id": ticket_id,
                "action": requested_action.value
            }
        )
    )
    logger.warning(
    "POLICY DECISION | ticket=%s | action=%s | allowed=%s | escalation=%s | reason=%s",
    ticket_id,
    decision.requested_action,
    decision.action_allowed,
    decision.security_escalation,
    decision.decision_reason
)

    return {
        "decision": decision,
        "workflow_logs": logs,
        "current_node": "verification_policy_node"
    }