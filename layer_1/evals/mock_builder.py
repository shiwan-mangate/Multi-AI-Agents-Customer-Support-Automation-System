import uuid
from datetime import datetime

def build_mock_ticket(case_id: str, input_text: str, metadata: dict = None)->dict:
    """
    Simulates a production 'Unified Ticket' from Layer 0.
    Ensures 100% schema alignment with the Supervisor Node.
    """
    metadata = metadata or {}
    cust_meta = metadata.get("customer_info", {})
    return {
        "ticket_id": case_id or str(uuid.uuid4()),

        "customer": {
            "user_id": cust_meta.get("user_id", "EVAL-USER-001"),
            "name": cust_meta.get("name", "Rahul"),
            "email": cust_meta.get("email", "rahul@test.com"),
            "tier": cust_meta.get("tier", "standard"),
            "lifetime_value": cust_meta.get("lifetime_value", 500),
            "previous_tickets": cust_meta.get("previous_tickets", 0)
        },

        "message": {
            "original": input_text,
            "normalized": input_text,
            "language": metadata.get("language", "english"),
            "detected_tone": metadata.get("detected_tone", "neutral")
        },

        "metadata": {
            "source": "eval_pipeline",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "priority": metadata.get("priority", "medium")
        },

        "status": "normalized"
    }