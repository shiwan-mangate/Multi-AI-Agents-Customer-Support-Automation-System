from layer_2_account_agent.schemas.account_state import AccountState
from layer_2_account_agent.schemas.domain import ActionType
from layer_2_account_agent.schemas.final_account_agent_responce import AccountAgentResponse
from pydantic import BaseModel
from typing import Optional, Dict, Any, Literal

def build_account_output(
    final_state: AccountState
) -> AccountAgentResponse:
    """
    Convert internal LangGraph state -> AccountAgentResponse
    This is the ONLY object exposed outside the Account Agent boundary.
    """

    decision = final_state.get("decision")
    provider_response = final_state.get("provider_response")

    # -------------------------------
    # 🟢 SAFE EXTRACTION: Decision
    # -------------------------------
    action_allowed = False
    decision_reason = None
    verification_level_val = None
    risk_level_val = None
    metrics = final_state.get("metrics")

    if decision:
        if isinstance(decision, dict):
            action_allowed = decision.get("action_allowed", False)
            decision_reason = decision.get("decision_reason")
            raw_vl = decision.get("verification_level")
            raw_rl = decision.get("risk_level")
        else:
            action_allowed = getattr(decision, "action_allowed", False)
            decision_reason = getattr(decision, "decision_reason", None)
            raw_vl = getattr(decision, "verification_level", None)
            raw_rl = getattr(decision, "risk_level", None)
            
        verification_level_val = raw_vl.value if hasattr(raw_vl, "value") else raw_vl
        risk_level_val = raw_rl.value if hasattr(raw_rl, "value") else raw_rl

    # -------------------------------
    # 🟢 SAFE EXTRACTION: Provider Response
    # -------------------------------
    provider_name = None
    provider_status = None
    provider_payload = None

    if provider_response:
        if isinstance(provider_response, dict):
            provider_name = provider_response.get("provider_name")
            raw_status = provider_response.get("status")
            provider_payload = provider_response.get("data")
        else:
            provider_name = getattr(provider_response, "provider_name", None)
            raw_status = getattr(provider_response, "status", None)
            provider_payload = getattr(provider_response, "data", None)
            
        provider_status = raw_status.value if hasattr(raw_status, "value") else raw_status

    # -------------------------------
    # Determine status
    # -------------------------------
    if final_state.get("clarification_required"):
        status = "clarification_required"
    elif final_state.get("security_escalation"):
        status = "escalated"
    elif decision and not action_allowed:
        status = "denied"
    else:
        status = "completed"

    # -------------------------------
    # Audit decision
    # -------------------------------
    audit_decision = None

    if final_state.get("duplicate_cached_response"):
        audit_decision = "duplicate_cached_response"
    elif final_state.get("security_escalation"):
        audit_decision = "security_escalated"
    elif decision and not action_allowed:
        audit_decision = "denied_by_policy"
    elif final_state.get("escalation_required"):
        audit_decision = "execution_failed"
    elif provider_response:
        audit_decision = "approved_and_executed"

    # -------------------------------
    # SAFE EXTRACTION: Enums
    # -------------------------------
    sub_cat = final_state.get("sub_category")
    sub_cat_val = sub_cat.value if hasattr(sub_cat, "value") else sub_cat

    req_action = final_state.get("requested_action")
    req_action_val = req_action.value if hasattr(req_action, "value") else req_action

    # -------------------------------
    # Build response
    # -------------------------------
    return AccountAgentResponse(
        # Metadata
        ticket_id=str(final_state.get("ticket_id")),
        customer_id=final_state.get("resolved_customer_id"),
        workflow_id=final_state.get("workflow_id", "UNKNOWN_WF"),
        correlation_id=final_state.get("correlation_id", "UNKNOWN_CORRELATION"),

        # Classification
        sub_category=sub_cat_val,
        requested_action=req_action_val,
        duration_ms=final_state.get("duration_ms"),

        # Decision
        status=status,
        decision_reason=decision_reason,
        verification_level=verification_level_val,
        risk_level=risk_level_val,

        # Execution
        execution_success=(provider_status == "SUCCESS" if provider_status else False),
        provider_name=provider_name,
        provider_status=provider_status,
        provider_response=provider_payload,

        # Customer-facing response
        customer_response=final_state.get("customer_response", ""),

        # Escalation
        escalation_required=final_state.get("escalation_required", False),
        security_escalation=final_state.get("security_escalation", False),
        escalation_reason=final_state.get("escalation_reason"),

        # Audit
        audit_decision=audit_decision,
        audit_logged=True
    )