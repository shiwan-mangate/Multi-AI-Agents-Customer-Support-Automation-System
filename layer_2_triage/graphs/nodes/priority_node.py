from datetime import datetime
from layer_2_triage.graphs.triage_state import TriageState

def priority_node(state: TriageState) -> TriageState:
    """
    Node Responsibility: Maps the numeric final_score to business priority labels.
    Refactored for consistency: Appending logs directly.
    """
    state["current_node"] = "priority_node"
    score = state.get("final_score")
    now = datetime.now()

    # 1. Fail-Safe: If score is missing, escalate immediately
    if score is None:
        state["final_priority"] = "high"
        state["escalation_required"] = True
        state["escalation_reason"] = "Priority mapping failure: Missing final_score"
        
        state["workflow_logs"].append({
            "timestamp": now.isoformat(),
            "node": "priority_node",
            "message": "Critical: Score missing. Reverting to safe-default High Priority.",
            "data": None
        })
        return state

    # 2. Deterministic Mapping
    if score >= 8.5:
        priority = "urgent"
    elif score >= 6.5:
        priority = "high"
    elif score >= 4.0:
        priority = "medium"
    else:
        priority = "low"

    # 3. Update State
    state["final_priority"] = priority

    # 4. Observability: Consistent append pattern
    state["workflow_logs"].append({
        "timestamp": now.isoformat(),
        "node": "priority_node",
        "message": f"Business priority successfully classified as {priority}.",
        "data": {
            "input_score": score,
            "assigned_priority": priority
        }
    })

    return state