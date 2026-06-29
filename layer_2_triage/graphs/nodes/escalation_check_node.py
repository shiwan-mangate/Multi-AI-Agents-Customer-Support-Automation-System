from datetime import datetime
from layer_2_triage.graphs.triage_state import TriageState, WorkflowLog

def escalation_check_node(state: TriageState) -> TriageState:
    """
    Centralized Escalation Policy Engine.
    Evaluates signals from previous nodes (Scoring, Ownership, Identity) 
    and determines if the ticket violates global business policy.
    """
    state["current_node"] = "escalation_check_node"
    
    # 1. Prepare signals
    try:
        confidence = float(state.get("supervisor_confidence", 1.0))
    except (ValueError, TypeError):
        confidence = 0.0 

    reasons = []
    
    # Check if a prior node already marked it as required
    if state.get("escalation_required") and state.get("escalation_reason"):
        reasons.append(state["escalation_reason"])

    tags = state.get("insight_tags", [])
    priority = (state.get("final_priority") or "low").lower()
    intent = state.get("initial_intent", "faq")
    customer_tier = (state.get("customer_tier") or "standard").lower()
    
    # Safely extract message text for keyword evaluation
    ticket = state.get("ticket", {})
    message = (ticket.get("message_english") or ticket.get("message_raw") or "").lower()

    # 2. Evaluation Logic (Business Policy)
    if "ownership_mismatch" in tags:
        reasons.append("Security Alert: Order/Customer ownership mismatch.")
    
    if not state.get("customer_id"):
        reasons.append("Identity Risk: Customer record not found.")

    if confidence < 0.65:
        reasons.append(f"Uncertainty: Low supervisor confidence ({confidence:.2f}).")

    if priority == "urgent" and "customer_contact_spike" in tags:
        reasons.append("High Churn Risk: Urgent priority + repeat contact spike.")
    
    if intent == "angry_complex":
        reasons.append("Complexity: High-sentiment/complex intent detected.")

    # =========================================================
    # 🟢 NEW: Escalation Keyword Triggers
    # =========================================================
    ESCALATION_KEYWORDS = [
        "manager",
        "supervisor",
        "escalate",
        "senior representative",
        "team lead"
    ]
    if any(word in message for word in ESCALATION_KEYWORDS):
        reasons.append("Customer explicitly requested supervisor escalation.")

    # 🟢 NEW: Duplicate Billing / Financial Dispute Triggers
    BILLING_KEYWORDS = [
        "charged twice",
        "double charged",
        "duplicate charge",
        "duplicate billing",
        "invoice"
    ]
    if any(word in message for word in BILLING_KEYWORDS):
        reasons.append("Financial dispute requires escalation review.")

    # 🟢 NEW: High Value Transaction Triggers
    if "high_value_transaction" in tags:
        reasons.append("High value transaction requires manual review.")

    # 🟢 NEW: Angry / High Priority Refund Trigger
    if intent == "refund_request" and priority in ["high", "urgent"]:
        reasons.append("High priority refund requires specialist review.")

    # 🟢 NEW: Enterprise Safety Rule
    if customer_tier == "enterprise" and priority in ["high", "urgent"]:
        reasons.append("Enterprise customer priority escalation.")

    # 3. Finalization
    if reasons:
        state["escalation_required"] = True
        # Deduplicate reasons while maintaining order
        state["escalation_reason"] = " | ".join(list(dict.fromkeys(reasons)))
    else:
        state["escalation_required"] = False
        state["escalation_reason"] = None

    # 4. Observability
    state["workflow_logs"].append({
        "timestamp": datetime.now().isoformat(),
        "node": "escalation_check_node",
        "message": "Global escalation policy evaluated.",
        "data": {
            "escalated": state["escalation_required"], 
            "active_triggers": reasons
        }
    })

    return state