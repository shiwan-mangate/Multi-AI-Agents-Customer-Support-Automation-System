from datetime import datetime
from layer_2_triage.graphs.triage_state import TriageState
from layer_2_triage.agents.scoring_engine import ScoringEngine

def scoring_node(state: TriageState) -> TriageState:
    """
    Node Responsibility: Executes the deterministic priority formula.
    Includes defensive error handling to prevent graph crashes during calculation.
    """
    state["current_node"] = "scoring_node"
    now = datetime.now()

    try:
        # 1. Execute Scoring Engine
        scorecard = ScoringEngine.get_full_scorecard(state)

        # 2. Map results back to state
        state["urgency_score"] = scorecard["urgency_score"]
        state["ltv_score"] = scorecard["ltv_score"]
        state["sentiment_score"] = scorecard["sentiment_score"]
        state["history_score"] = scorecard["history_score"]
        state["final_score"] = scorecard["final_score"]

        # 3. Observability: Consistent direct-append logging
        state["workflow_logs"].append({
            "timestamp": now.isoformat(),
            "node": "scoring_node",
            "message": f"Deterministic scoring complete. Final Score: {state['final_score']}",
            "data": scorecard
        })

        return state

    except Exception as e:
        # 4. Resilience: Fail-safe to manual triage on math error
        state["escalation_required"] = True
        state["escalation_reason"] = "Internal scoring failure"
        
        state["workflow_logs"].append({
            "timestamp": now.isoformat(),
            "node": "scoring_node",
            "message": "Scoring engine failure. Reverting to manual triage.",
            "data": {"error": str(e)}
        })
        return state