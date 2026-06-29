# tests/fixtures/escalation_payloads.py

ESCALATION_SUCCESS_OUTPUT = {
    "status": "ESCALATED",
    "ticket_id": 4001,
    "case_id": "esc-8f3c2ab91d44",
    "source_agent": "triage_agent",
    "response": {
        "priority": "MEDIUM",
        "assigned_team": "retention_team",
        "holding_sent": True
    }
}

ESCALATION_DUPLICATE_OUTPUT = {
    "status": "DUPLICATE_SUPPRESSED",
    "ticket_id": 4002,
    "case_id": "esc-8f3c2ab91d44",
    "source_agent": "escalation_agent",
    "response": {
        "priority": "HIGH",
        "assigned_team": "support_team",
        "holding_sent": False
    }
}

ESCALATION_REVIEW_OUTPUT = {
    "status": "HUMAN_REVIEW_REQUIRED",
    "ticket_id": 4003,
    "case_id": "esc-999xyz",
    "source_agent": "refund_agent",
    "response": {
        "priority": "CRITICAL",
        "assigned_team": "fraud_team",
        "holding_sent": True
    }
}

ESCALATION_FAILED_OUTPUT = {
    "status": "FAILED",
    "ticket_id": 4004,
    "source_agent": "triage_agent",
    "response": {
        "error_message": "Routing engine timed out connecting to Zendesk API."
    }
}