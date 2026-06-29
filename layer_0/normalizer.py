## layer_0/normalizer.py
import uuid
from datetime import datetime, timezone

def normalize(data: dict):
    message = (data.get("message") or "").strip()

    if not message:
        message = "No message provided"

    customer_id = int(data["customer_id"])

    customer_name = (
        data.get("name")
        or data.get("customer_name")
        or "unknown"
    ).strip()

    ticket_id = data.get("ticket_id") or f"TKT-{uuid.uuid4().hex[:12].upper()}"

    timestamp = datetime.now(
        timezone.utc
    ).isoformat()

    channel = data.get("channel", "web")

    normalized_data = {
    "ticket_id": ticket_id,
    "channel": channel,
    "customer_id": customer_id,
    "customer_name": customer_name,
    "timestamp": timestamp,
    "issue_description": message,
    "message_text": message,

    "conversation_history": data.get(
        "conversation_history",
        []
    ),

    "language": "unknown",
    "intent": None,
    "order_id": None,
    "issue_type": None,
    "customer_info": None,
}

    return normalized_data