from datetime import datetime
from layer_2_triage.graphs.triage_state import TriageState
from layer_2_triage.repositories.customer_repository import CustomerRepository

def fetch_customer_node(state: TriageState) -> TriageState:
    """
    Lean Node: Responsible ONLY for identity resolution and basic CRM LTV/Tier.
    Aligned with 'customers' schema (bigint/numeric).
    """
    state["current_node"] = "fetch_customer_node"
    repo = CustomerRepository()

    try:
        email = state.get("customer_email")
        customer = repo.get_customer_by_email(email)

        # 1. Identity Guard: Handle unknown customer
        if not customer:
            state["escalation_required"] = True
            state["escalation_reason"] = "Customer record not found in CRM"
            state["final_priority"] = "high"
            
            state["workflow_logs"].append({
                "timestamp": datetime.now().isoformat(),
                "node": "fetch_customer_node",
                "message": "Unknown customer. Flagging for high-priority review.",
                "data": {"email": email}
            })
            return state

        # 2. Identity Resolution & Context Enrichment
        customer_id = customer["customer_id"]
        context = repo.get_triage_context(customer_id)
        
        # 3. State Update (Mapping to CRM context)
        state["customer_id"] = customer_id
        state["customer_tier"] = context["account_tier"]
        state["ltv"] = float(context["ltv"] or 0.0) # Numeric -> Float
        state["total_tickets"] = context["total_tickets"]
        state["total_escalations"] = context["total_escalations"]

        state["workflow_logs"].append({
            "timestamp": datetime.now().isoformat(),
            "node": "fetch_customer_node",
            "message": "CRM identity and LTV successfully loaded.",
            "data": {"customer_id": customer_id, "tier": state["customer_tier"]}
        })

        return state

    except Exception as e:
        # 4. Resilience: Handle DB errors gracefully
        state["escalation_required"] = True
        state["escalation_reason"] = "Internal CRM enrichment failure"
        
        state["workflow_logs"].append({
            "timestamp": datetime.now().isoformat(),
            "node": "fetch_customer_node",
            "message": f"DB Error: {str(e)}", 
            "data": {"error_type": type(e).__name__}
        })
        return state

    finally:
        repo.close()