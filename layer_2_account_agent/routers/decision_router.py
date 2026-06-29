from layer_2_account_agent.schemas.account_state import AccountState
from layer_2_account_agent.schemas.domain import ActionType


def clarification_router(state: AccountState) -> str:
    if state.get("clarification_required"):
        return "response_generation"

    return "identity_resolution"


def execution_router(state: AccountState) -> str:
    if state.get("duplicate_cached_response"):
        return "audit_log"

    decision = state.get("decision")

    if not decision:
        return "audit_log"

    if decision.security_escalation:
        return "security_escalation"

    if not decision.action_allowed:
        return "audit_log"

    if decision.requested_action == ActionType.PASSWORD_RESET:
        return "password_reset"

    elif decision.requested_action == ActionType.ACCOUNT_UNLOCK:
        return "unlock_account"

    elif decision.requested_action == ActionType.INVOICE_RETRIEVAL:
        return "invoice_retrieval"

    elif decision.requested_action == ActionType.BILLING_EXPLANATION:
        return "billing_history"

    return "audit_log"