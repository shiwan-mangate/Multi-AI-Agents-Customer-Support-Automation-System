from datetime import datetime, UTC
from typing import Dict, Any

from layer_2_proactive_agent.schemas.proactive_state import (
    ProactiveState,
)
from layer_2_proactive_agent.schemas.proactive_output import (
    ProactiveOutput,
)
from layer_2_proactive_agent.schemas.enums import (
    OutreachStatus,
)
from layer_2_proactive_agent.utils.logger import (
    logger,
)


def response_node(state: ProactiveState) -> Dict[str, Any]:
    """
    Final API Boundary Node.
    Packages the internal LangGraph state into the 
    public ProactiveOutput contract.

    Verified against DB constraints:
    - customer_id -> bigint (int)
    - workflow_id -> character varying (str)
    """
    workflow_id = state["workflow_id"]

    logger.info(
        "Status=START | Node=RESPONSE | Workflow=%s",
        workflow_id,
    )

    timestamp = datetime.now(UTC).isoformat()

    try:
        # 1. Extract path-dependent context from LangGraph state
        signal = state.get("signal")
        suppressed = state.get("suppressed", False)
        
        signal_assessment = state.get("signal_assessment")
        risk_assessment = state.get("risk_assessment")
        decision = state.get("decision")
        
        outreach_message = state.get("outreach_message")
        escalation_handoff = state.get("escalation_handoff")

        # Fallback customer_id to ensure type safety with bigint
        customer_id = signal.customer_id if signal else -1

        # 2. Determine Final Status Mapping
        if suppressed:
            final_status = OutreachStatus.SUPPRESSED
            
        elif decision:
            # Defensive check to extract value whether it arrives as an Enum or a string literal
            action_obj = getattr(decision, "action", None)
            action_val = action_obj.value if hasattr(action_obj, "value") else str(action_obj)
            
            if action_val == "OUTREACH":
                final_status = OutreachStatus.OUTREACH_CREATED
                
            elif action_val == "ESCALATE":
                final_status = OutreachStatus.ESCALATION_REQUIRED
                
            else:
                final_status = OutreachStatus.NO_ACTION
                
        else:
            raise ValueError(
                "Unable to determine OutreachStatus: "
                "No decision or suppression flag found in state."
            )

        # 3. Construct Final Validated Contract Payload
        output_payload = ProactiveOutput(
            workflow_id=workflow_id,
            agent_id="proactive_agent",
            status=final_status,
            customer_id=customer_id,
            signal_assessment=signal_assessment,
            risk_assessment=risk_assessment,
            decision=decision,
            outreach_message=outreach_message,
            escalation_handoff=escalation_handoff,
        )

        logger.info(
            "Status=SUCCESS | Node=RESPONSE | Workflow=%s | FinalStatus=%s",
            workflow_id,
            final_status.value,
        )

        return {
            "output": output_payload,
            "current_node": "response_node",
            "workflow_logs": [
                {
                    "timestamp": timestamp,
                    "node": "response_node",
                    "message": (
                        f"Workflow completed for "
                        f"customer={customer_id} with "
                        f"status={final_status.value}"
                    ),
                }
            ],
        }

    except Exception as exc:
        logger.exception(
            "Status=FAILED | Node=RESPONSE | Workflow=%s | Error=%s",
            workflow_id,
            str(exc),
        )
        raise