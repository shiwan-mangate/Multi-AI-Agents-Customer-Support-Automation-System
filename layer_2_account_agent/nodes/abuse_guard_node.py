import logging
from typing import Dict, Any

from layer_2_account_agent.schemas.account_state import AccountState
from layer_2_account_agent.schemas.domain import WorkflowLog
from layer_2_account_agent.services.abuse_guard import (
    AbuseGuardService,
    AbuseAssessment
)

logger = logging.getLogger(__name__)


def abuse_guard(
    state: AccountState,
    abuse_guard_service: AbuseGuardService
) -> Dict[str, Any]:
    """
    Node 6: Operational abuse analysis.

    Evaluates operational abuse risk.
    If detected, escalates to security agent.
    If not detected, continues workflow.

    """

    ticket_id = state.get("ticket_id")
    auth_context = state.get("auth_context")

    logs = list(state.get("workflow_logs", []))

    triage_context = {
        "unresolved_repeat_count": state.get("unresolved_repeat_count", 0),
        "total_tickets": state.get("total_tickets", 0),
        "total_escalations": state.get("total_escalations", 0)
    }

    logger.info(
        "Executing abuse_guard node ticket_id=%s",
        ticket_id
    )

    try:
        result = abuse_guard_service.evaluate_abuse(
            auth_context=auth_context,
            triage_context=triage_context
        )

        logs.append(
            WorkflowLog(
                node="abuse_guard_node",
                message=(
                    f"Abuse analysis complete "
                    f"detected={result.abuse_detected} "
                    f"score={result.abuse_score}"
                ),
                data={
                    "ticket_id": ticket_id,
                    "reason": result.reason
                }
            )
        )

        return {
            "abuse_assessment": result,
            "workflow_logs": logs,
            "current_node": "abuse_guard_node"
        }

    except Exception:
        logger.exception(
            "Abuse analysis failed ticket_id=%s",
            ticket_id
        )

        fallback = AbuseAssessment(
            abuse_detected=False,
            abuse_score=0.0,
            signals={"system_failure": True},
            reason="Abuse analysis unavailable"
        )

        logs.append(
            WorkflowLog(
                node="abuse_guard_node",
                message="Abuse analysis failed. Safe fallback applied.",
                data={
                    "ticket_id": ticket_id
                }
            )
        )

        return {
            "abuse_assessment": fallback,
            "workflow_logs": logs,
            "current_node": "abuse_guard_node"
        }