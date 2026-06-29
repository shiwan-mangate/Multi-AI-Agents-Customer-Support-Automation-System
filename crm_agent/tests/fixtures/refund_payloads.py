# tests/fixtures/refund_payloads.py

REFUND_AUTO_APPROVE_OUTPUT = {
    "ticket_id": "TKT-2001",
    "workflow_id": "WF-9b3d112a",
    "assigned_agent": "refund_agent",
    "status": "resolved",
    "resolution": {
        "resolution_type": "refund_completed",
        "message": "Your refund has been approved and processed successfully.",
        "refund_amount": 120.0,
        "currency": "USD",
        "transaction_id": "TXN-A9D44211"
    },
    "decision": {
        "final_status": "COMPLETED",
        "decision_code": "REFUND_EXECUTED",
        "decision_reason": "Criteria met. Auto-approval granted."
    },
    "audit": {
        "audit_status": "SUCCESS",
        "idempotency_key": "IDEM-8391aa21",
        "review_required": False
    }
}

REFUND_HUMAN_REVIEW_OUTPUT = {
    "ticket_id": "TKT-2002",
    "workflow_id": "WF-2a5ccf0f",
    "assigned_agent": "refund_agent",
    "status": "resolved",
    "resolution": {
        "resolution_type": "refund_completed",
        "message": "Your refund has been successfully processed following management review.",
        "refund_amount": 650.0,
        "currency": "USD",
        "transaction_id": "TXN-146C31FE"
    },
    "decision": {
        "final_status": "COMPLETED",
        "decision_code": "REFUND_EXECUTED",
        "decision_reason": "Human Review Result: APPROVE"
    },
    "audit": {
        "audit_status": "SUCCESS",
        "idempotency_key": "IDEM-2498a6c5",
        "review_required": True
    }
}

REFUND_REJECTED_OUTPUT = {
    "ticket_id": "TKT-2003",
    "workflow_id": "WF-a82d91c2",
    "assigned_agent": "refund_agent",
    "status": "closed",
    "resolution": {
        "resolution_type": "refund_rejected",
        "message": "We are unable to process this refund because the eligibility period has expired."
    },
    "decision": {
        "final_status": "REJECTED",
        "decision_code": "OUTSIDE_WINDOW",
        "decision_reason": "Refund period of 30 days has expired."
    },
    "audit": {
        "audit_status": "SUCCESS",
        "idempotency_key": "IDEM-f8829a1d",
        "review_required": False
    }
}

REFUND_IDEMPOTENT_OUTPUT = {
    "ticket_id": "TKT-2004",
    "workflow_id": "WF-2a5ccf0f",
    "assigned_agent": "refund_agent",
    "status": "resolved",
    "resolution": {
        "resolution_type": "refund_completed",
        "message": "This refund request was already processed earlier.",
        "refund_amount": 120.0,
        "currency": "USD",
        "transaction_id": "TXN-A9D44211"
    },
    "decision": {
        "final_status": "COMPLETED",
        "decision_code": "IDEMPOTENT_REPLAY",
        "decision_reason": "Refund already processed."
    },
    "audit": {
        "audit_status": "SUCCESS",
        "idempotency_key": "IDEM-8391aa21",
        "review_required": False
    }
}