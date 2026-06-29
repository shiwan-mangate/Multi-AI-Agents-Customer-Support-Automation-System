# tests/fixtures/account_payloads.py

ACCOUNT_PASSWORD_RESET_OUTPUT = {
    "ticket_id": 3001,
    "source_agent": "account_agent",
    "status": "completed",
    "request": {
        "intent": "account_issue",
        "requested_action": "password_reset"
    },
    "decision": {
        "action_allowed": True,
        "verification_level": "PASSED",
        "risk_level": "LOW",
        "decision_reason": "Policy approved execution"
    },
    "customer_response": "Password reset link sent.",
    "audit": {
        "decision_type": "approved_and_executed"
    }
}

ACCOUNT_ESCALATION_OUTPUT = {
    "ticket_id": 3002,
    "agent": "account_agent",
    "status": "escalated",
    "request": {
        "intent": "account_issue",
        "requested_action": "account_unlock"
    },
    "decision": {
        "action_allowed": False,
        "verification_level": "FAILED",
        "risk_level": "CRITICAL",
        "decision_reason": "Multiple failed identity verification attempts."
    },
    "customer_response": "For your security, I am transferring you to a human specialist to unlock your account.",
    "audit": {
        "decision_type": "security_lockout"
    }
}

ACCOUNT_DENIED_OUTPUT = {
    "ticket_id": 3003,
    "agent": "account_agent",
    "status": "denied",
    "request": {
        "intent": "billing_issue",
        "requested_action": "tier_upgrade"
    },
    "decision": {
        "action_allowed": False,
        "verification_level": "FAILED",
        "risk_level": "LOW",
        "decision_reason": "Payment method declined by processor."
    },
    "customer_response": "Your tier upgrade was denied because the payment method on file was declined."
}