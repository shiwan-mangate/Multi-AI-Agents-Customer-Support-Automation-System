# tests/fixtures/common.py

from datetime import datetime, UTC

GLOBAL_CONTEXT = {
    "customer_id": 10592,
    "customer_email": "enterprise_user@example.com",
    "tier": "enterprise",
    "ltv": 12500.00,
    "ticket_id": "TKT-1001",
    "ticket_created_at": datetime.now(UTC),
    "channel": "web_chat",
    "query_intent": "refund_request",
    "sentiment_start": "frustrated",
    "language": "en",
    "issue_tags": ["payment_issue"],
    "conversation_history": [
        {
            "role": "user",
            "content": "I was double charged for my subscription and I want a refund immediately.",
            "timestamp": "2026-05-29T10:00:00Z"
        },
        {
            "role": "agent",
            "content": "I can certainly look into that for you right now.",
            "timestamp": "2026-05-29T10:00:05Z"
        }
    ]
}