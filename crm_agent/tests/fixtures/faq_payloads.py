# tests/fixtures/faq_payloads.py

FAQ_SUCCESS_OUTPUT = {
    "ticket_id": "TKT-1001",
    "assigned_agent": "faq_agent",
    "status": "resolved",
    "resolution": {
        "resolution_type": "faq_answer",
        "message": "Yes, opened items can be returned within 30 days of delivery as long as they are in good condition with original packaging."
    },
    "decisioning": {
        "decision_target": "customer",
        "confidence_score": 0.97,
        "knowledge_gap_detected": False,
        "escalation_required": False
    },
    "execution_metadata": {
        "query_intent": "Return Policy"
    },
    "audit": {
        "handled_by": "faq_agent"
    }
}

FAQ_CLARIFICATION_OUTPUT = {
    "ticket_id": "TKT-1002",
    "assigned_agent": "faq_agent",
    "status": "clarification_required",
    "clarification": {
        "question": "Could you clarify which product or order you are referring to?"
    },
    "decisioning": {
        "decision_target": "customer",
        "knowledge_gap_detected": False,
        "escalation_required": False
    },
    "audit": {
        "handled_by": "faq_agent",
        "paused_for_human_input": True
    }
}

FAQ_KNOWLEDGE_GAP_OUTPUT = {
    "ticket_id": "TKT-1003",
    "assigned_agent": "faq_agent",
    "status": "handoff",
    "resolution": {
        "resolution_type": "knowledge_gap",
        "message": "The FAQ knowledge base does not contain sufficient information to answer this question."
    },
    "decisioning": {
        "decision_target": "escalation_agent",
        "confidence_score": 0.0,
        "knowledge_gap_detected": True,
        "escalation_required": True
    },
    "audit": {
        "handled_by": "faq_agent"
    }
}