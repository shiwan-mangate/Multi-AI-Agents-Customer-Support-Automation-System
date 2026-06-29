from layer_2_account_agent.schemas.account_state import AccountState
from layer_2_account_agent.schemas.domain import WorkflowLog, RiskAssessment, RiskLevel
from layer_2_account_agent.services.risk_engine import RiskEngineService
import logging
from typing import Dict, Any
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


def risk_assessment(
    state: AccountState
) -> Dict[str, Any]:
    """
    Risk aggregation engine.
    """

    ticket_id = state.get("ticket_id")
    abuse_assessment = state.get("abuse_assessment")
    takeover_assessment = state.get("takeover_assessment")
    requested_action = state.get("requested_action")

    logs = list(state.get("workflow_logs", []))

    triage_context = {
        "ltv": state.get("ltv"),
        "unresolved_repeat_count": state.get("unresolved_repeat_count"),
        "total_tickets": state.get("total_tickets"),
        "total_escalations": state.get("total_escalations")
    }

    logger.info(
        "Executing risk_assessment node ticket_id=%s",
        ticket_id
    )

    if not requested_action:
        fallback = RiskAssessment(
        risk_score=100.0,
        risk_level=RiskLevel.HIGH,
        takeover_detected=False,
        abuse_detected=False,
        signals={"missing_action": True}
    )

        return {
            "risk_assessment": fallback,
            "current_node": "risk_assessment_node"
        }

    try:
        risk_engine = RiskEngineService()

        result = risk_engine.calculate_risk(
            triage_context=triage_context,
            requested_action=requested_action,
            abuse_assessment=abuse_assessment,
            takeover_assessment=takeover_assessment
        )

        logs.append(
        WorkflowLog(
        node="risk_assessment_node",
        message=(
            f"Risk assessment complete "
            f"score={result.risk_score} "
            f"level={result.risk_level.value}"
        ),
        timestamp=datetime.now(timezone.utc),
        data={
            "ticket_id": ticket_id,
            "risk_score": result.risk_score,
            "risk_level": result.risk_level.value,
            "takeover_detected": result.takeover_detected,
            "abuse_detected": result.abuse_detected
        }
    )
)

        return {
            "risk_assessment": result,
            "workflow_logs": logs,
            "current_node": "risk_assessment_node"
        }

    except Exception:
        logger.exception(
            "Risk assessment failed ticket_id=%s",
            ticket_id
        )

        fallback = RiskAssessment(
        risk_score=100.0,
        risk_level=RiskLevel.HIGH,
        takeover_detected=False,
        abuse_detected=False,
        signals={"system_failure": True}
    )

        return {
            "risk_assessment": fallback,
            "workflow_logs": logs,
            "current_node": "risk_assessment_node"
        }