import pytest
from unittest.mock import patch, MagicMock
from layer_2_proactive_agent.graph.proactive_graph import proactive_graph
from layer_2_proactive_agent.schemas.enums import OutreachStatus, OutreachAction
from layer_2_proactive_agent.schemas.proactive_state import ProactiveState
from crm_agent.schemas.crm_event import CRMResolvedEvent
from datetime import datetime, UTC

# ---------------------------------------------------------
# Test: Full Outreach Happy Path (Integration)
# ---------------------------------------------------------

# 1. Patch DB Classes (These nodes were refactored to remove globals)
@patch("layer_2_proactive_agent.nodes.customer_context_node.SessionLocal")
@patch("layer_2_proactive_agent.nodes.customer_context_node.CustomerProfileRepository")
@patch("layer_2_proactive_agent.nodes.suppression_gate_node.SessionLocal")
@patch("layer_2_proactive_agent.nodes.suppression_gate_node.ProactiveOutreachRepository")
@patch("layer_2_proactive_agent.nodes.suppression_gate_node.SuppressionService")

# 2. Patch Global Instances (These nodes still use global instantiations)
@patch("layer_2_proactive_agent.nodes.signal_analysis_node.signal_detection_service")
@patch("layer_2_proactive_agent.nodes.risk_scoring_node.risk_engine")
@patch("layer_2_proactive_agent.nodes.outreach_decision_node.decision_service")
@patch("layer_2_proactive_agent.nodes.message_generation_node.message_generation_service")
def test_full_outreach_flow_happy_path(
    mock_msg_svc,
    mock_decision_svc,
    mock_risk_engine,
    mock_signal_svc,
    
    mock_suppression_svc_class,
    mock_outreach_repo_class,
    mock_suppression_session,
    
    mock_customer_repo_class,
    mock_customer_session,
    
    sample_signal,
    sample_customer_profile,
    sample_signal_assessment,
    sample_risk_assessment,
    sample_outreach_decision,
    sample_outreach_message,
):
    """
    Integration test: Runs the full graph from START to END.
    Validates state transitions and ensures every node in the 
    chain is invoked exactly once.
    """

    # 1. Setup Service Mocks
    mock_customer_repo = mock_customer_repo_class.return_value
    
    # Replicated flat ORM database record representation matching your table schema
    mock_orm_profile = MagicMock()
    mock_orm_profile.customer_id = sample_customer_profile.customer_id
    mock_orm_profile.customer_email = sample_customer_profile.customer_email
    mock_orm_profile.tier = sample_customer_profile.tier
    mock_orm_profile.ltv = sample_customer_profile.ltv
    
    mock_orm_profile.total_tickets = sample_customer_profile.total_tickets
    mock_orm_profile.total_faq_tickets = sample_customer_profile.total_faq_tickets
    mock_orm_profile.total_refund_tickets = sample_customer_profile.total_refund_tickets
    mock_orm_profile.total_account_tickets = sample_customer_profile.total_account_tickets
    
    mock_orm_profile.total_escalations = sample_customer_profile.total_escalations
    mock_orm_profile.total_denials = sample_customer_profile.total_denials
    mock_orm_profile.total_failures = sample_customer_profile.total_failures
    mock_orm_profile.total_clarifications = sample_customer_profile.total_clarifications
    mock_orm_profile.total_duplicate_suppressions = sample_customer_profile.total_duplicate_suppressions
    
    mock_orm_profile.repeat_negative_count = sample_customer_profile.repeat_negative_count
    mock_orm_profile.repeat_escalation_count = sample_customer_profile.repeat_escalation_count
    mock_orm_profile.duplicate_request_count = sample_customer_profile.duplicate_request_count
    mock_orm_profile.negative_ticket_count = sample_customer_profile.negative_ticket_count
    
    # Specific outreach evaluation properties
    mock_orm_profile.last_sentiment = "negative"
    mock_orm_profile.sentiment_history = ["negative"]
    mock_orm_profile.churn_score = 85
    mock_orm_profile.churn_level = "HIGH"
    mock_orm_profile.churn_last_updated = sample_customer_profile.updated_at
    
    mock_orm_profile.issue_frequency = {}
    mock_orm_profile.agent_interaction_frequency = {}
    mock_orm_profile.languages_used = ["en"]
    mock_orm_profile.preferred_language = "en"
    
    mock_orm_profile.first_seen_at = sample_customer_profile.created_at
    mock_orm_profile.last_ticket_at = sample_customer_profile.updated_at
    mock_orm_profile.updated_at = sample_customer_profile.updated_at

    mock_customer_repo.get_profile.return_value = mock_orm_profile
    
    mock_suppression_svc = mock_suppression_svc_class.return_value
    mock_suppression_svc.should_suppress.return_value = (False, None)
    
    mock_signal_svc.analyze.return_value = sample_signal_assessment
    mock_risk_engine.assess.return_value = sample_risk_assessment
    mock_decision_svc.decide.return_value = sample_outreach_decision
    mock_msg_svc.generate.return_value = sample_outreach_message

    # 2. Define Initial State
    initial_state: ProactiveState = {
        "workflow_id": "WF-E2E-001",
        "signal_id": sample_signal.signal_id,
        "status": "ACTIVE",
        "signal": sample_signal,
        "customer_profile": None,
        "signal_assessment": None,
        "risk_assessment": None,
        "decision": None,
        "outreach_message": None,
        "escalation_handoff": None,
        "crm_event": CRMResolvedEvent.model_construct(
            event={"id": "dummy"},
            ticket={"id": "dummy"},
            customer={"id": 123},
            resolution={"status": "resolved"},
            risk={"score": 99}
        ),
        "output": None,
        "suppressed": False,
        "suppression_reason": None,
        "current_node": None,
        "workflow_logs": [],
        "errors": [],
    }

    # 3. Execute Graph
    config = {"configurable": {"thread_id": "test_outreach_flow"}}
    result = proactive_graph.invoke(initial_state, config=config)

    # 4. Assert Service Invocations (Proof of Traversal)
    mock_customer_repo.get_profile.assert_called_once()
    mock_suppression_svc.should_suppress.assert_called_once()
    mock_signal_svc.analyze.assert_called_once()
    mock_risk_engine.assess.assert_called_once()
    mock_decision_svc.decide.assert_called_once()
    mock_msg_svc.generate.assert_called_once()

    # 5. Assert Final Output State
    output = result["output"]
    assert output.status == OutreachStatus.OUTREACH_CREATED
    assert output.customer_id == sample_signal.customer_id
    
    # Assert pipeline integrity
    assert output.risk_assessment is not None
    assert output.signal_assessment is not None
    assert output.decision is not None
    assert output.outreach_message is not None
    
    # 6. Assert Observability (Workflow log completion)
    assert len(result["workflow_logs"]) > 0
    assert result["workflow_logs"][-1]["node"] == "response_node"