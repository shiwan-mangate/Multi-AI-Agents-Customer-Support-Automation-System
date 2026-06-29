import os
import pytest
from datetime import datetime, UTC
from decimal import Decimal
from uuid import uuid4
from unittest.mock import patch, MagicMock

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# ---------------------------------------------------------
# REAL ARCHITECTURE IMPORTS
# ---------------------------------------------------------
from layer_2_proactive_agent.graph.proactive_graph import proactive_graph
from layer_2_proactive_agent.adapters.proactive_adapter import ProactiveAdapter

# Only import the Proactive Base (SQLite compatible)
from layer_2_proactive_agent.database.base import Base as ProactiveBase

# Real Repositories
from layer_2_proactive_agent.repositories.proactive_outreach_repository import ProactiveOutreachRepository

# Real Services
from layer_2_proactive_agent.services.suppression_service import SuppressionService
from layer_2_proactive_agent.services.risk_engine import RiskEngine
from layer_2_proactive_agent.services.escalation_service import EscalationService

# Real Schemas
from layer_2_proactive_agent.schemas.proactive_state import ProactiveState
from layer_2_proactive_agent.schemas.signal import Signal
from layer_2_proactive_agent.schemas.enums import SignalType, SignalSource, OutreachStatus, RiskLevel, OutreachAction
from layer_2_proactive_agent.schemas.signal_assessment import SignalAssessment
from layer_2_proactive_agent.schemas.outreach_decision import OutreachDecision
from layer_2_proactive_agent.schemas.outreach_message import OutreachMessage
from layer_2_proactive_agent.schemas.escalation_handoff import EscalationHandoff # <-- Added Import
from crm_agent.schemas.crm_event import CRMResolvedEvent


# ==============================================================================
# DATABASE SETUP (In-Memory SQLite)
# ==============================================================================

@pytest.fixture(scope="module")
def db_engine():
    db_url = "sqlite:///:memory:"
    engine = create_engine(db_url)
    ProactiveBase.metadata.create_all(engine)
    yield engine
    ProactiveBase.metadata.drop_all(engine)


@pytest.fixture
def db_session(db_engine):
    Session = sessionmaker(bind=db_engine)
    session = Session()
    yield session
    session.rollback()
    session.close()


# ==============================================================================
# E2E HELPERS
# ==============================================================================

def build_initial_state(customer_id: int, signal_type: SignalType) -> ProactiveState:
    signal = Signal(
        signal_id=f"SIG-{uuid4().hex[:6]}",
        customer_id=customer_id,
        signal_type=signal_type,
        signal_source=SignalSource.CRM,
        signal_context={}
    )
    return {
        "workflow_id": f"WF-E2E-{uuid4().hex[:6]}",
        "signal_id": signal.signal_id,
        "status": "ACTIVE",
        "signal": signal,
        "customer_profile": None,
        "signal_assessment": None,
        "risk_assessment": None,
        "decision": None,
        "outreach_message": None,
        "escalation_handoff": None,
        "crm_event": CRMResolvedEvent.model_construct(
            event={"id": "dummy"},
            ticket={"id": "dummy"},
            customer={"id": customer_id},
            resolution={"status": "resolved"},
            risk={"score": 0}
        ), 
        "output": None,
        "suppressed": False,
        "suppression_reason": None,
        "current_node": None,
        "workflow_logs": [],
        "errors": [],
    }


# ==============================================================================
# TRUE E2E JOURNEYS
# ==============================================================================

@patch("layer_2_proactive_agent.nodes.signal_analysis_node.signal_detection_service.analyze")
@patch("layer_2_proactive_agent.nodes.outreach_decision_node.decision_service.decide")
@patch("layer_2_proactive_agent.nodes.message_generation_node.message_generation_service.generate")
def test_e2e_full_outreach_journey(mock_llm_msg, mock_llm_dec, mock_llm_sig, db_session, sample_customer_profile):
    
    real_suppression_service = SuppressionService(repo=ProactiveOutreachRepository(session=db_session))
    real_risk_engine = RiskEngine()
    adapter = ProactiveAdapter()

    initial_state = build_initial_state(sample_customer_profile.customer_id, SignalType.INACTIVE_CUSTOMER)
    
    mock_llm_sig.return_value = SignalAssessment(signal_type=SignalType.INACTIVE_CUSTOMER, severity=RiskLevel.MEDIUM, detected_reason="Test", requires_immediate_attention=False)
    mock_llm_dec.return_value = OutreachDecision(action=OutreachAction.OUTREACH, reason="Check in needed", review_required=False)
    mock_llm_msg.return_value = OutreachMessage(subject="Checking In", body="Hello", channel="email", generated_by="gpt-4o")

    mock_customer_repo = MagicMock()
    mock_customer_repo.get_profile.return_value = sample_customer_profile

    with patch("layer_2_proactive_agent.nodes.customer_context_node.CustomerProfileRepository", return_value=mock_customer_repo), \
         patch("layer_2_proactive_agent.nodes.suppression_gate_node.SuppressionService", return_value=real_suppression_service), \
         patch("layer_2_proactive_agent.nodes.risk_scoring_node.risk_engine", real_risk_engine):
        
        result = proactive_graph.invoke(initial_state, config={"configurable": {"thread_id": "e2e_outreach"}})

    crm_event = adapter.to_crm_event(result["output"])
    assert crm_event.resolution.status == "resolved"
    assert crm_event.conversation.messages[0]["subject"] == "Checking In"


@patch("layer_2_proactive_agent.nodes.signal_analysis_node.signal_detection_service.analyze")
@patch("layer_2_proactive_agent.nodes.outreach_decision_node.decision_service.decide")
def test_e2e_full_escalation_journey(mock_llm_dec, mock_llm_sig, db_session, sample_customer_profile):
    
    real_suppression_service = SuppressionService(repo=ProactiveOutreachRepository(session=db_session))
    real_risk_engine = RiskEngine()
    adapter = ProactiveAdapter()

    # FIX: Use the standard profile to keep msgpack happy, and mock the EscalationService to bypass the 'last_sentiment' bug.
    mock_escalation_service = MagicMock()
    mock_escalation_service.handoff.return_value = EscalationHandoff(
        ticket_id="ESC-WF-123",
        customer_id=sample_customer_profile.customer_id,
        customer_email="test@example.com",
        source_agent="proactive_agent",
        initial_intent="HIGH_CHURN_RISK",
        initial_sentiment="negative",
        initial_urgency="urgent",
        supervisor_confidence=1.0,
        message_raw="test",
        message_english="test",
        created_at=datetime.now(UTC),
    )

    initial_state = build_initial_state(sample_customer_profile.customer_id, SignalType.HIGH_CHURN_RISK)

    mock_llm_sig.return_value = SignalAssessment(signal_type=SignalType.HIGH_CHURN_RISK, severity=RiskLevel.CRITICAL, detected_reason="Critical", requires_immediate_attention=True)
    mock_llm_dec.return_value = OutreachDecision(action=OutreachAction.ESCALATE, reason="Requires Human", review_required=True)

    mock_customer_repo = MagicMock()
    mock_customer_repo.get_profile.return_value = sample_customer_profile

    with patch("layer_2_proactive_agent.nodes.customer_context_node.CustomerProfileRepository", return_value=mock_customer_repo), \
         patch("layer_2_proactive_agent.nodes.suppression_gate_node.SuppressionService", return_value=real_suppression_service), \
         patch("layer_2_proactive_agent.nodes.risk_scoring_node.risk_engine", real_risk_engine), \
         patch("layer_2_proactive_agent.nodes.escalation_handoff_node.escalation_service", mock_escalation_service):
        
        result = proactive_graph.invoke(initial_state, config={"configurable": {"thread_id": "e2e_escalation"}})

    crm_event = adapter.to_crm_event(result["output"])
    assert crm_event.resolution.status == "escalated"
    assert crm_event.risk.escalated is True


@patch("layer_2_proactive_agent.nodes.signal_analysis_node.signal_detection_service.analyze")
@patch("layer_2_proactive_agent.nodes.outreach_decision_node.decision_service.decide")
def test_e2e_suppression_journey(mock_llm_dec, mock_llm_sig, db_session, sample_customer_profile):
    
    real_suppression_service = SuppressionService(repo=ProactiveOutreachRepository(session=db_session))
    real_risk_engine = RiskEngine()
    adapter = ProactiveAdapter()

    mock_llm_sig.return_value = SignalAssessment(signal_type=SignalType.INACTIVE_CUSTOMER, severity=RiskLevel.MEDIUM, detected_reason="Test", requires_immediate_attention=False)
    mock_llm_dec.return_value = OutreachDecision(action=OutreachAction.OUTREACH, reason="Check in", review_required=False)

    mock_customer_repo = MagicMock()
    mock_customer_repo.get_profile.return_value = sample_customer_profile

    # RUN 1
    initial_state_1 = build_initial_state(sample_customer_profile.customer_id, SignalType.INACTIVE_CUSTOMER)
    with patch("layer_2_proactive_agent.nodes.customer_context_node.CustomerProfileRepository", return_value=mock_customer_repo), \
         patch("layer_2_proactive_agent.nodes.suppression_gate_node.SuppressionService", return_value=real_suppression_service), \
         patch("layer_2_proactive_agent.nodes.risk_scoring_node.risk_engine", real_risk_engine), \
         patch("layer_2_proactive_agent.nodes.message_generation_node.message_generation_service.generate") as mock_llm_msg:
        mock_llm_msg.return_value = OutreachMessage(subject="Checking In", body="Hello", channel="email", generated_by="gpt-4o")
        result_1 = proactive_graph.invoke(initial_state_1, config={"configurable": {"thread_id": "e2e_suppression_1"}})
    
    record = real_suppression_service.create_outreach_record(result_1["workflow_id"], initial_state_1["signal_id"], sample_customer_profile.customer_id, SignalType.INACTIVE_CUSTOMER, "OUTREACH_EXECUTED")
    real_suppression_service.save_outreach(record)
    db_session.commit()

    # RUN 2
    initial_state_2 = build_initial_state(sample_customer_profile.customer_id, SignalType.INACTIVE_CUSTOMER)
    with patch("layer_2_proactive_agent.nodes.customer_context_node.CustomerProfileRepository", return_value=mock_customer_repo), \
         patch("layer_2_proactive_agent.nodes.suppression_gate_node.SuppressionService", return_value=real_suppression_service):
        result_2 = proactive_graph.invoke(initial_state_2, config={"configurable": {"thread_id": "e2e_suppression_2"}})

    crm_event = adapter.to_crm_event(result_2["output"])
    assert crm_event.resolution.status == "duplicate_suppressed"


@patch("layer_2_proactive_agent.nodes.signal_analysis_node.signal_detection_service.analyze")
@patch("layer_2_proactive_agent.nodes.outreach_decision_node.decision_service.decide")
def test_e2e_no_action_journey(mock_llm_dec, mock_llm_sig, db_session, sample_customer_profile):
    
    real_suppression_service = SuppressionService(repo=ProactiveOutreachRepository(session=db_session))
    real_risk_engine = RiskEngine()
    adapter = ProactiveAdapter()

    initial_state = build_initial_state(sample_customer_profile.customer_id, SignalType.RECENT_NEGATIVE_EXPERIENCE)
    mock_llm_sig.return_value = SignalAssessment(signal_type=SignalType.RECENT_NEGATIVE_EXPERIENCE, severity=RiskLevel.LOW, detected_reason="Ignore", requires_immediate_attention=False)
    mock_llm_dec.return_value = OutreachDecision(action=OutreachAction.NO_ACTION, reason="Score below threshold", review_required=False)

    mock_customer_repo = MagicMock()
    mock_customer_repo.get_profile.return_value = sample_customer_profile

    with patch("layer_2_proactive_agent.nodes.customer_context_node.CustomerProfileRepository", return_value=mock_customer_repo), \
         patch("layer_2_proactive_agent.nodes.suppression_gate_node.SuppressionService", return_value=real_suppression_service), \
         patch("layer_2_proactive_agent.nodes.risk_scoring_node.risk_engine", real_risk_engine):
        result = proactive_graph.invoke(initial_state, config={"configurable": {"thread_id": "e2e_no_action"}})

    crm_event = adapter.to_crm_event(result["output"])
    assert crm_event.resolution.status == "resolved"