from datetime import datetime, timedelta
from layer_2_triage.graphs.triage_state import TriageState

def sla_node(state: TriageState) -> TriageState:
    """
    Node Responsibility: Maps classification to a time-based commitment.
    Aligns business priority with operational deadlines.
    """
    state["current_node"] = "sla_node"
    now = datetime.now()
    
    # 1. Extraction & Normalization
    priority_raw = state.get("final_priority")
    priority = priority_raw.lower() if priority_raw else None
    
    tier = (state.get("customer_tier") or "standard").lower()
    channel = (state.get("ticket", {}).get("channel") or "web").lower()
    
    # 2. Fail-Safe: Missing Priority
    if not priority:
        state["sla_duration_hours"] = 4
        state["sla_deadline"] = now + timedelta(hours=4)
        state["escalation_required"] = True
        state["escalation_reason"] = "SLA assignment fallback: Missing priority"
        
        state["workflow_logs"].append({
            "timestamp": now.isoformat(),
            "node": "sla_node",
            "message": "Priority missing. Applied safe-default 4h SLA and flagged for review.",
            "data": None
        })
        return state

    # 3. Deterministic SLA Calculation
    base_mapping = {
        "urgent": 2,
        "high": 4,
        "medium": 24,
        "low": 48
    }
    sla_hours = base_mapping.get(priority, 24)

    # 4. Business Policy Overrides
    if tier == "enterprise" and priority == "high":
        sla_hours = 2
    elif tier == "premium" and priority == "medium":
        sla_hours = 12
        
    # 5. Operational Hard-Cap for Chat
    if channel == "chat" and sla_hours > 6:
        sla_hours = 6

    # 6. Finalize SLA state
    state["sla_duration_hours"] = sla_hours
    state["sla_deadline"] = now + timedelta(hours=sla_hours)

    # 7. Observability: Consistent direct-append logging
    state["workflow_logs"].append({
        "timestamp": now.isoformat(),
        "node": "sla_node",
        "message": f"SLA commitment of {sla_hours}h assigned.",
        "data": {
            "priority": priority,
            "tier": tier,
            "channel": channel,
            "deadline": state["sla_deadline"].isoformat()
        }
    })

    return state