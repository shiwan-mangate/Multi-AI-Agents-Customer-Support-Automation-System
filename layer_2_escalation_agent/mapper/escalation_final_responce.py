import logging
from layer_2_escalation_agent.schemas.escalation_output import EscalationAgentResponse

logger = logging.getLogger(__name__)

def build_escalation_output(
    final_state: dict,
    thread_id: str | None = None,
    review_payload: dict | None = None,
    error: str | None = None,
) -> EscalationAgentResponse:
    """
    Convert LangGraph state dictionary to a validated EscalationAgentResponse contract.
    Ensures Pydantic verification guarantees are satisfied across execution flows.
    """
    
    # ---------------------------------------------------
    # STATUS RESOLUTION
    # ---------------------------------------------------
    # 1. Prioritize explicit interruption payloads or errors
    logger.warning(
    "ESCALATION FINAL STATE duration_ms = %s",
    final_state.get("duration_ms"),
)
    metrics = final_state.get("metrics")
    if review_payload:
        status_str = "HUMAN_REVIEW_REQUIRED"
        
    elif error:
        status_str = "FAILED"
        
    # 2. Resolve background graph statuses
    else:
        raw_status = (
            final_state.get("status") 
            or final_state.get("audit_status")
        )
        
        if raw_status and str(raw_status).lower() == "persisted":
            status_str = "COMPLETED"
            
        elif final_state.get("response") is not None:
            status_str = "COMPLETED"
            
        # Catch-all to preserve explicit statuses like DUPLICATE_SUPPRESSED
        elif raw_status:
            status_str = str(raw_status).upper()
            
        else:
            status_str = "IN_PROGRESS"

    # Contract guardrail
    if status_str == "COMPLETED" and final_state.get("response") is None:
        raise ValueError(
            "Completed escalation missing response object."
        )
        
    logger.warning(
        "MAPPER DECISION = %s",
        final_state.get("human_decision")
    )
    
    agent_response = EscalationAgentResponse(
        ticket_id=str(final_state.get("ticket_id", "")),
        source_agent=final_state.get("source_agent", "unknown"),
        thread_id=thread_id,
        duration_ms=final_state.get("duration_ms"),
        status=status_str,  
        response=final_state.get("response"),
        review_payload=review_payload,
        error=error,
    )

    # =======================================================
    # 🟢 Reconstruct the missing customer message 
    # =======================================================
    logger.warning(
        "MAPPER DECISION TYPE = %s",
        type(final_state.get("human_decision"))
    )

    logger.warning(
        "MAPPER DECISION VALUE = %s",
        final_state.get("human_decision")
    )
    
    human_decision = final_state.get("human_decision")
    holding_message = final_state.get("holding_message")

    logger.warning(
        "MAPPER HUMAN DECISION TYPE = %s",
        type(human_decision)
    )
    logger.warning(
        "MAPPER HUMAN DECISION = %s",
        human_decision
    )
    
    if human_decision:
        # 1. Safely extract the raw decision target (might be string, dict, or Enum)
        decision_val = None
        if isinstance(human_decision, dict):
            decision_val = human_decision.get("decision")
        elif hasattr(human_decision, "decision"):
            decision_val = human_decision.decision
        else:
            decision_val = human_decision

        # 2. 🟢 UNIVERSAL ENUM CHECK: Extract the underlying string if it's an Enum
        if hasattr(decision_val, "value"):
            decision_val = decision_val.value

        # 3. Now string conversion is perfectly safe!
        decision_upper = str(decision_val).strip().upper() if decision_val else ""

        # ==============================================
        # 🟢 INJECTED DIAGNOSTIC TELEMETRY
        # ==============================================
        logger.warning(
            "MAPPER HUMAN DECISION RAW = %s",
            human_decision
        )

        logger.warning(
            "MAPPER DECISION_VAL = %s",
            decision_val
        )

        logger.warning(
            "MAPPER DECISION_UPPER = %s",
            decision_upper
        )

        logger.warning(
            "MAPPER DECISION_UPPER REPR = %r",
            decision_upper
        )
        # ==============================================

        if decision_upper == "APPROVE":
            msg = "Your escalated request has been manually reviewed and approved by our management team. We are taking action immediately."
        elif decision_upper == "REJECT":
            msg = "We have carefully reviewed your escalated request. Unfortunately, after manual management review, we are unable to approve the request at this time."
        else:
            msg = f"Your escalated request has been reviewed. Result: {decision_upper}"
    else:
        # Fallback for pauses or unreviewed completions
        msg = holding_message or "Your request has been escalated to our specialist team for further review."

    # Graft the message onto the object safely
    agent_response.customer_facing_response = msg

    logger.info(f"Escalation Mapper | Attached final customer message: {msg}")

    return agent_response