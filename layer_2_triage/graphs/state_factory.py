from datetime import datetime
from typing import Dict, Any
from layer_2_triage.graphs.triage_state import TriageState, TicketPayload, ExtractedEntities, WorkflowLog

class TriageStateFactory:
    """
    Standardizes the entry point for the Triage Agent.
    Maintains a strict data contract between Layer 1 and Layer 2.
    """

    @staticmethod
    def create_triage_state(l1_data: Dict[str, Any]) -> TriageState:
        print("\n========== L1 INPUT ==========")
        print(l1_data)
        print("==============================\n")


        now = datetime.now()
        
        
        confidence = float(l1_data.get("confidence", 0.0))
        if confidence > 1.0:
            confidence = confidence / 100.0

  
        raw_entities = l1_data.get("entities", {})
        print("\n========== RAW ENTITIES ==========")
        print(raw_entities)
        print("==================================\n")

        entities: ExtractedEntities = {
    "order_id": raw_entities.get("order_id"),

    # Preserve None instead of converting it to the string "None"
    "product_name": raw_entities.get("product_name"),

    "amount": (
        float(raw_entities.get("amount"))
        if raw_entities.get("amount") is not None
        else None
    ),

    "purchase_date": raw_entities.get("purchase_date"),

    "shipping_address": raw_entities.get("shipping_address")
}

        print("\n========== STATE ENTITIES ==========")
        print(entities)
        print("====================================\n")
        

        ticket_payload: TicketPayload = {
            "ticket_id": str(l1_data.get("ticket_id", "UNKNOWN")),
            "channel": str(l1_data.get("channel", "web")),
            "customer_id": str(l1_data.get("customer_id", "UNKNOWN")),
            "message_raw": str(l1_data.get("message_raw", "")),
            "message_english": str(l1_data.get("message_english", "")),
            "timestamp": now
        }
        
        
        initial_log: WorkflowLog = {
            "timestamp": now.isoformat(),
            "node": "state_factory",
            "message": f"Workflow initialized for ticket {l1_data.get('ticket_id')}.",
            "data": {"initial_intent": l1_data.get("intent")}
        }

       
        return {
            "ticket": ticket_payload,
            "entities": entities,
            "ticket_id": str(l1_data.get("ticket_id", "UNKNOWN")),
            "customer_email": str(l1_data.get("customer_email", "")), 
            "customer_id": None, 
            "initial_intent": str(l1_data.get("intent", "faq")),
            
            "initial_urgency": str(l1_data.get("urgency", "medium")),
            "initial_sentiment": str(l1_data.get("sentiment", "neutral")),
            "supervisor_confidence": confidence,

          
            "customer_tier": None,
            "ltv": 0.0,
            "unresolved_repeat_count": 0,
            "total_tickets": 0,
            "total_escalations": 0,
            "last_sentiment": None,
            "order_context": None,

            
            "urgency_score": None,
            "ltv_score": None,
            "sentiment_score": None,
            "history_score": None,
            "final_score": None,

            
            "final_priority": None,
            "sla_duration_hours": None,
            "sla_deadline": None,

           
            "insight_tags": [],
            "escalation_required": False,
            "escalation_reason": None,

          
            "created_at": now,
            "next_agent": None, 
            "current_node": "START",
            "workflow_logs": [initial_log]
        }