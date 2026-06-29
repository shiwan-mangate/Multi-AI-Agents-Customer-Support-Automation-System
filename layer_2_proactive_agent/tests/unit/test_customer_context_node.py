import pytest
from unittest.mock import patch, MagicMock

from layer_2_proactive_agent.nodes.customer_context_node import (
    customer_context_node,
)

def _to_flat_orm_mock(pydantic_profile):
    flat_row = MagicMock()
    flat_row.customer_id = pydantic_profile.customer_id
    flat_row.customer_email = pydantic_profile.customer_email
    flat_row.tier = pydantic_profile.tier
    flat_row.ltv = pydantic_profile.ltv
    flat_row.total_tickets = pydantic_profile.total_tickets
    flat_row.total_faq_tickets = pydantic_profile.total_faq_tickets
    flat_row.total_refund_tickets = pydantic_profile.total_refund_tickets
    flat_row.total_account_tickets = pydantic_profile.total_account_tickets
    flat_row.total_escalations = pydantic_profile.total_escalations
    flat_row.total_denials = pydantic_profile.total_denials
    flat_row.total_failures = pydantic_profile.total_failures
    flat_row.total_clarifications = pydantic_profile.total_clarifications
    flat_row.total_duplicate_suppressions = pydantic_profile.total_duplicate_suppressions
    flat_row.repeat_negative_count = pydantic_profile.repeat_negative_count
    flat_row.repeat_escalation_count = pydantic_profile.repeat_escalation_count
    flat_row.duplicate_request_count = pydantic_profile.duplicate_request_count
    flat_row.negative_ticket_count = pydantic_profile.negative_ticket_count
    
    flat_row.last_sentiment = pydantic_profile.sentiment_profile.last_sentiment
    flat_row.sentiment_history = pydantic_profile.sentiment_profile.sentiment_history
    flat_row.churn_score = pydantic_profile.churn_intelligence.churn_score
    flat_row.churn_level = pydantic_profile.churn_intelligence.churn_level
    flat_row.churn_last_updated = pydantic_profile.churn_intelligence.churn_last_updated
    
    flat_row.issue_frequency = pydantic_profile.issue_tags
    flat_row.agent_interaction_frequency = pydantic_profile.agent_interactions
    flat_row.languages_used = pydantic_profile.languages_used
    flat_row.preferred_language = pydantic_profile.preferred_language
    
    flat_row.first_seen_at = pydantic_profile.first_seen_at
    flat_row.last_ticket_at = pydantic_profile.last_ticket_at
    flat_row.updated_at = pydantic_profile.updated_at
    return flat_row


@patch("layer_2_proactive_agent.nodes.customer_context_node.SessionLocal")
@patch("layer_2_proactive_agent.nodes.customer_context_node.CustomerProfileRepository")
def test_customer_context_happy_path(
    mock_repo_class,
    mock_session_local,
    sample_proactive_state,
    sample_customer_profile,
):
    state = sample_proactive_state.copy()
    state["customer_profile"] = None
    customer_id = state["signal"].customer_id
    
    flat_db_row = _to_flat_orm_mock(sample_customer_profile)
    mock_repo_instance = mock_repo_class.return_value
    mock_repo_instance.get_profile.return_value = flat_db_row

    result = customer_context_node(state=state)

    mock_session_local.assert_called_once()
    mock_repo_class.assert_called_once()
    mock_repo_instance.get_profile.assert_called_once_with(customer_id)
    
    assert result["current_node"] == "customer_context_node"
    assert result["customer_profile"].customer_id == sample_customer_profile.customer_id
    assert result["customer_profile"].customer_email == sample_customer_profile.customer_email
    assert len(result["workflow_logs"]) == 1
    assert "customer profile loaded" in result["workflow_logs"][0]["message"].lower()


@patch("layer_2_proactive_agent.nodes.customer_context_node.SessionLocal")
@patch("layer_2_proactive_agent.nodes.customer_context_node.CustomerProfileRepository")
def test_customer_context_log_structure(
    mock_repo_class,
    mock_session_local,
    sample_proactive_state,
    sample_customer_profile,
):
    flat_db_row = _to_flat_orm_mock(sample_customer_profile)
    mock_repo_instance = mock_repo_class.return_value
    mock_repo_instance.get_profile.return_value = flat_db_row

    result = customer_context_node(state=sample_proactive_state)
    log = result["workflow_logs"][0]

    assert "timestamp" in log
    assert "node" in log
    assert "message" in log
    assert log["node"] == "customer_context_node"


@patch("layer_2_proactive_agent.nodes.customer_context_node.SessionLocal")
@patch("layer_2_proactive_agent.nodes.customer_context_node.CustomerProfileRepository")
def test_customer_context_profile_not_found(
    mock_repo_class,
    mock_session_local,
    sample_proactive_state,
):
    state = sample_proactive_state.copy()
    state["customer_profile"] = None
    
    mock_repo_instance = mock_repo_class.return_value
    mock_repo_instance.get_profile.return_value = None

    with pytest.raises(ValueError, match="not found"):
        customer_context_node(state=state)


@patch("layer_2_proactive_agent.nodes.customer_context_node.SessionLocal")
@patch("layer_2_proactive_agent.nodes.customer_context_node.CustomerProfileRepository")
def test_customer_context_database_error(
    mock_repo_class,
    mock_session_local,
    sample_proactive_state,
):
    state = sample_proactive_state.copy()
    state["customer_profile"] = None
    
    mock_repo_instance = mock_repo_class.return_value
    mock_repo_instance.get_profile.side_effect = Exception("Database connection lost.")

    with pytest.raises(Exception, match="Database connection lost."):
        customer_context_node(state=state)


def test_customer_context_missing_signal(sample_proactive_state):
    state = sample_proactive_state.copy()
    state["signal"] = None

    with pytest.raises(AttributeError):
        customer_context_node(state=state)


def test_customer_context_invalid_customer_id(sample_proactive_state):
    state = sample_proactive_state.copy()
    state["signal"] = state["signal"].model_copy(update={"customer_id": 0})

    with pytest.raises(ValueError, match="Invalid customer_id"):
        customer_context_node(state=state)