from datetime import datetime
from layer_2_triage.graphs.triage_state import TriageState, WorkflowLog

def dispatch_node(state: TriageState) -> TriageState:
    """
    Thin Dispatcher: Executes routing based on finalized flags.
    Synchronized with centralized escalation policy.
    """

    state["current_node"] = "dispatch_node"
    intent = state.get("initial_intent", "faq").lower()

    # 1. Policy-driven escalation
    if state.get("escalation_required"):
        next_agent = "escalation_agent"
        reason = (
            f"Policy escalation: "
            f"{state.get('escalation_reason', 'Manual review required')}"
        )

    # 2. Standard Routing
    else:

        # Refund validation gate
        if (
            intent == "refund_request"
            and not state.get("entities", {}).get("order_id")
        ):
            state["escalation_required"] = True
            state["escalation_reason"] = (
                "Refund request missing order_id"
            )

            next_agent = "escalation_agent"
            reason = (
                "Refund request requires order_id."
            )

        else:
            intent_map = {
                "refund_request": "refund_agent",
                "account_issue": "account_agent",
                "technical_bug": "tech_bug_agent",
                "faq": "faq_agent"
            }

            next_agent = intent_map.get(
                intent,
                "escalation_agent"
            )

            reason = (
                f"Specialist route: {intent}"
                if intent in intent_map
                else "Unknown intent fallback"
            )

    state["next_agent"] = next_agent

    log: WorkflowLog = {
        "timestamp": datetime.now().isoformat(),
        "node": "dispatch_node",
        "message": f"Ticket dispatched to {next_agent}.",
        "data": {
            "decision_reason": reason,
            "target_agent": next_agent
        }
    }

    state["workflow_logs"].append(log)

    return state