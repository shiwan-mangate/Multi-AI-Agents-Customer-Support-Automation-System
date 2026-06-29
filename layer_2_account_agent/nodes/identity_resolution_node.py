from layer_2_account_agent.schemas.account_state import AccountState
from layer_2_account_agent.schemas.domain import WorkflowLog, VerificationLevel
from layer_2_account_agent.services.identity_service import IdentityService
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)


def identity_resolution(
    state: AccountState,
    identity_service: IdentityService
) -> Dict[str, Any]:
    """
    Node 4: Zero-trust identity verification.
    """

    ticket_id = state.get("ticket_id")
    customer_email = state.get("customer_email")
    triage_customer_id = state.get("customer_id")
    entities = state.get("entities")

    logger.info(
        "Executing identity_resolution node ticket_id=%s",
        ticket_id
    )

    logs = list(state.get("workflow_logs", []))

    try:
        result = identity_service.resolve_identity(
            email=customer_email,
            triage_customer_id=triage_customer_id,
            entities=entities
        )
        logger.warning(
    "IDENTITY RESULT | ticket=%s | verified=%s | confidence=%s | level=%s | resolved_customer=%s | signals=%s",
    ticket_id,
    result.identity_verified,
    result.identity_confidence,
    result.verification_level,
    result.resolved_customer_id,
    result.identity_signals
)

        logs.append(
            WorkflowLog(
                node="identity_resolution_node",
                message=(
                    f"Identity resolution complete "
                    f"verified={result.identity_verified} "
                    f"confidence={result.identity_confidence}"
                ),
                data={
                    "ticket_id": ticket_id,
                    "resolved_customer_id": result.resolved_customer_id
                }
            )
        )

        return {
            "identity_verified": result.identity_verified,
            "identity_confidence": result.identity_confidence,
            "resolved_customer_id": result.resolved_customer_id,
            "identity_signals": result.identity_signals,
            "verification_level": result.verification_level,
            "workflow_logs": logs,
            "current_node": "identity_resolution_node"
        }

    except Exception:
        logger.exception(
            "Identity resolution failed ticket_id=%s",
            ticket_id
        )

        logs.append(
            WorkflowLog(
                node="identity_resolution_node",
                message=(
                    "Identity resolution failed. "
                    "Security fallback applied."
                ),
                data={
                    "ticket_id": ticket_id
                }
            )
        )

        return {
            "identity_verified": False,
            "identity_confidence": 0.0,
            "resolved_customer_id": None,
            "identity_signals": {
                "system_failure": True
            },
            "verification_level": VerificationLevel.FAILED,
            "workflow_logs": logs,
            "current_node": "identity_resolution_node"
        }