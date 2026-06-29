from datetime import datetime
from layer_2_triage.graphs.triage_state import TriageState
from layer_2_triage.repositories.ticket_repository import TicketRepository

# Threshold for detecting abnormal contact patterns
SPIKE_THRESHOLD = 3 

def history_node(state: TriageState) -> TriageState:
    """
    Node Responsibility: Behavioral signals (Unresolved repeats, spikes, sentiment trend).
    Analyzes historical ticket data to flag behavioral risks.
    """
    state["current_node"] = "history_node"
    
    # 1. Identity Guard
    if not state.get("customer_id"):
        state["workflow_logs"].append({
            "timestamp": datetime.now().isoformat(),
            "node": "history_node",
            "message": "Skipping history lookup: No valid customer_id found.",
            "data": None 
        })
        return state

    repo = TicketRepository()

    try:
        customer_id = state["customer_id"]
        intent = state["initial_intent"]
        
        # 2. Historical Aggregation
        unresolved_repeats = repo.count_unresolved_repeat_issues(customer_id, intent)
        recent_volume = repo.get_recent_ticket_count(customer_id, days=14)
        last_sentiment = repo.get_last_ticket_sentiment(customer_id)

        # 3. Behavioral Spike Detection
        if recent_volume >= SPIKE_THRESHOLD:
            if "customer_contact_spike" not in state["insight_tags"]:
                state["insight_tags"].append("customer_contact_spike")

        # 4. State Update
        state["unresolved_repeat_count"] = unresolved_repeats
        state["last_sentiment"] = last_sentiment

        state["workflow_logs"].append({
            "timestamp": datetime.now().isoformat(),
            "node": "history_node",
            "message": "Historical behavioral signals successfully analyzed.",
            "data": {
                "unresolved_repeats": unresolved_repeats,
                "spike_detected": recent_volume >= SPIKE_THRESHOLD,
                "historical_sentiment": last_sentiment
            }
        })

        return state

    except Exception as e:
        state["workflow_logs"].append({
            "timestamp": datetime.now().isoformat(),
            "node": "history_node",
            "message": "Internal history retrieval failure.",
            "data": {"error_detail": str(e)}
        })
        return state

    finally:
        repo.close()