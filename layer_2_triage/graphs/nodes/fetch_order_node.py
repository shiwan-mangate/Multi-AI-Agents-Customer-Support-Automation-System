from datetime import datetime
from layer_2_triage.graphs.triage_state import TriageState, WorkflowLog, OrderContext
from layer_2_triage.repositories.order_repository import OrderRepository

HIGH_VALUE_THRESHOLD = 500.0

def fetch_order_node(state: TriageState) -> TriageState:
    """
    Node Responsibility: Transactional enrichment with strict ownership validation.
    Restored security audit logging for production observability.
    """
    state["current_node"] = "fetch_order_node"
    
    order_id = state.get("entities", {}).get("order_id")
    if not order_id:
        state["workflow_logs"].append({
            "timestamp": datetime.now().isoformat(),
            "node": "fetch_order_node",
            "message": "No order_id provided. Skipping transaction lookup.",
            "data": None
        })
        return state

    repo = OrderRepository()
    try:
        order_data = repo.get_order_by_id(order_id)

        if not order_data:

            if "order_lookup_failed" not in state["insight_tags"]:
                state["insight_tags"].append("order_lookup_failed")

            state["workflow_logs"].append({
                "timestamp": datetime.now().isoformat(),
                "node": "fetch_order_node",
                "message": f"Order {order_id} not found in database.",
                "data": {"order_id": order_id}
            })

            return state

        # Security: Ownership Validation
        resolved_customer_id = state.get("customer_id")
        if resolved_customer_id and order_data["customer_id"] != resolved_customer_id:
            if "ownership_mismatch" not in state["insight_tags"]:
                state["insight_tags"].append("ownership_mismatch")
            
            # Restored Forensic Audit Log
            state["workflow_logs"].append({
                "timestamp": datetime.now().isoformat(),
                "node": "fetch_order_node",
                "message": "SECURITY ALERT: Order ownership mismatch.",
                "data": {
                    "order_id": order_id,
                    "expected_customer": resolved_customer_id,
                    "actual_customer": order_data["customer_id"]
                }
            })
            return state

        # Mapping: Created_at passed as datetime object
        context: OrderContext = {
            "order_id": order_data["order_id"],
            "amount": float(order_data["order_amount"]), 
            "status": str(order_data["order_status"]).upper(), 
            "created_at": order_data["created_at"] 
        }
        state["order_context"] = context

        # Signal Generation
        if context["status"] in ["DELAYED", "PROCESSING"]:
            if "logistics_stalled" not in state["insight_tags"]:
                state["insight_tags"].append("logistics_stalled")
        
        if context["amount"] >= HIGH_VALUE_THRESHOLD:
            if "high_value_transaction" not in state["insight_tags"]:
                state["insight_tags"].append("high_value_transaction")

        state["workflow_logs"].append({
            "timestamp": datetime.now().isoformat(),
            "node": "fetch_order_node",
            "message": f"Transaction context for {order_id} loaded.",
            "data": {"order_id": context["order_id"]}
        })

        return state

    except Exception as e:
        state["workflow_logs"].append({
            "timestamp": datetime.now().isoformat(),
            "node": "fetch_order_node",
            "message": "Internal error during order lookup.",
            "data": {"error": str(e)}
        })
        return state
    finally:
        repo.close()