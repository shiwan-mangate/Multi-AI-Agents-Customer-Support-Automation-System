# tests/integration/test_alert_flow.py

import pytest
from unittest.mock import MagicMock
from datetime import datetime, UTC
from decimal import Decimal

from crm_agent.services.alerts.alert_service import AlertService
from crm_agent.services.alerts.slack_notifier import SlackNotifier
from crm_agent.repositories.churn_alert_repository import ChurnAlertRepository

from crm_agent.schemas.crm_event import (
    CRMResolvedEvent,
    EventMetadata,
    TicketMetadata,
    CustomerMetadata,
    ResolutionMetadata,
    RiskMetadata,
    DecisionMetadata,
    AnalyticsMetadata,
    ConversationMetadata,
)
from crm_agent.schemas.churn import (
    ChurnAssessment,
    ChurnComputationBreakdown,
)
from crm_agent.db.models.churn_alert_model import ChurnAlert


# =========================================================
# Helpers
# =========================================================
def build_event(tier: str = "standard") -> CRMResolvedEvent:
    return CRMResolvedEvent(
        event=EventMetadata(
            event_id="evt_alert_test",
            event_type="ticket.resolved",
            source_agent="refund_agent",
            schema_version="1.0.0",
            created_at=datetime.now(UTC),
        ),
        ticket=TicketMetadata(ticket_id="TKT-ALERT", channel="web"),
        customer=CustomerMetadata(
            customer_id=1,
            customer_email="test@example.com",
            tier=tier,
            ltv=Decimal("100.00"),
        ),
        resolution=ResolutionMetadata(
            status="resolved",
            resolution_type="refund_completed",
            resolved_by="refund_agent",
        ),
        decision=DecisionMetadata(decision_code="REFUND_EXECUTED", review_required=False),
        risk=RiskMetadata(escalated=False, risk_level="LOW"),
        analytics=AnalyticsMetadata(
            intent="refund_request",
            issue_tags=["refund"],
            sentiment_start="angry",
            sentiment_end="angry",
        ),
        conversation=ConversationMetadata(
            messages=[],
            agents_involved=["refund_agent"],
            original_message="Refund request",
        ),
    )


def build_assessment(churn_level: str, score: float) -> ChurnAssessment:
    return ChurnAssessment(
        customer_id=1,
        churn_score=Decimal(str(score)),
        churn_level=churn_level,
        risk_reasons=[
            "Repeated escalations",
            "Negative sentiment trend",
        ],
        breakdown=ChurnComputationBreakdown(
            final_score=Decimal(str(score))
        ),
    )


def build_db_alert(alert_type: str = "CHURN_RISK") -> ChurnAlert:
    return ChurnAlert(
        alert_id="alert_001",
        customer_id=1,
        ticket_id="TKT-100",
        customer_email="test@example.com",
        tier="premium",
        ltv=Decimal("1500.00"),
        source_agent="refund_agent",
        alert_type=alert_type,
        severity="HIGH",
        score=Decimal("85.00"),
        reason="Customer at risk",
        risk_reasons=[
            "Repeated escalations",
            "Negative sentiment",
        ],
        alert_status="OPEN",
        delivery_status="PENDING",
        acknowledged=False,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )


# =========================================================
# Fixtures
# =========================================================
@pytest.fixture
def alert_env():
    mock_repo = MagicMock(spec=ChurnAlertRepository)
    alert_service = AlertService(alert_repo=mock_repo)
    notifier = SlackNotifier(alert_repo=mock_repo)
    return {
        "service": alert_service,
        "notifier": notifier,
        "repo": mock_repo
    }


# =========================================================
# 1. Alert Generation Logic
# =========================================================
def test_critical_risk_generates_alert(alert_env):
    env = alert_env
    event = build_event()
    assessment = build_assessment("CRITICAL", 95.0)
    
    env["repo"].get_open_alert.return_value = None
    env["repo"].create_alert.return_value = build_db_alert()

    alert = env["service"].create_alert_if_needed(event, assessment)

    assert alert is not None
    env["repo"].create_alert.assert_called_once()


def test_high_risk_generates_alert(alert_env):
    env = alert_env
    event = build_event()
    assessment = build_assessment("HIGH", 75.0)
    
    env["repo"].get_open_alert.return_value = None
    env["repo"].create_alert.return_value = build_db_alert()

    alert = env["service"].create_alert_if_needed(event, assessment)

    assert alert is not None
    env["repo"].create_alert.assert_called_once()


def test_medium_risk_skips_alert(alert_env):
    env = alert_env
    event = build_event()
    assessment = build_assessment("MEDIUM", 45.0)

    alert = env["service"].create_alert_if_needed(event, assessment)

    assert alert is None
    env["repo"].create_alert.assert_not_called()


def test_low_risk_skips_alert(alert_env):
    env = alert_env
    event = build_event()
    assessment = build_assessment("LOW", 15.0)

    alert = env["service"].create_alert_if_needed(event, assessment)

    assert alert is None
    env["repo"].create_alert.assert_not_called()


# =========================================================
# 2. Suppression Logic
# =========================================================
def test_existing_alert_suppresses_new_alert(alert_env):
    env = alert_env
    event = build_event()
    assessment = build_assessment("HIGH", 75.0)
    
    env["repo"].get_open_alert.return_value = build_db_alert()

    alert = env["service"].create_alert_if_needed(event, assessment)

    assert alert is None
    env["repo"].create_alert.assert_not_called()


# =========================================================
# 3. VIP Routing Logic
# =========================================================
def test_premium_customer_generates_vip_alert(alert_env):
    env = alert_env
    event = build_event()
    event.customer.tier = "premium"
    assessment = build_assessment("CRITICAL", 92.0)
    
    env["repo"].get_open_alert.return_value = None
    env["repo"].create_alert.return_value = build_db_alert("VIP_CHURN_RISK")

    env["service"].create_alert_if_needed(event, assessment)

    kwargs = env["repo"].create_alert.call_args.kwargs
    assert kwargs["alert_type"] == "VIP_CHURN_RISK"


def test_standard_customer_generates_normal_alert(alert_env):
    env = alert_env
    event = build_event()
    event.customer.tier = "standard"
    assessment = build_assessment("HIGH", 80.0)
    
    env["repo"].get_open_alert.return_value = None
    env["repo"].create_alert.return_value = build_db_alert("CHURN_RISK")

    env["service"].create_alert_if_needed(event, assessment)

    kwargs = env["repo"].create_alert.call_args.kwargs
    assert kwargs["alert_type"] == "CHURN_RISK"


# =========================================================
# 4. Slack Notifier Pipeline
# =========================================================
def test_successful_alert_dispatch(alert_env):
    env = alert_env
    alert = build_db_alert()
    
    env["notifier"]._send = MagicMock()

    result = env["notifier"].dispatch_alert(alert)

    assert result is True
    env["repo"].mark_delivery_sent.assert_called_once_with(alert.alert_id)


def test_failed_alert_dispatch(alert_env):
    env = alert_env
    alert = build_db_alert()
    
    env["notifier"]._send = MagicMock(side_effect=Exception("Slack API Timeout"))

    result = env["notifier"].dispatch_alert(alert)

    assert result is False
    env["repo"].mark_delivery_failed.assert_called_once_with(alert.alert_id)


def test_alert_message_formatting():
    notifier = SlackNotifier(alert_repo=MagicMock())
    alert = build_db_alert()

    message = notifier._build_alert_message(alert)

    assert "Customer ID" in message
    assert str(alert.customer_id) in message
    assert alert.alert_type.replace("_", " ") in message
    assert alert.severity in message
    assert "Repeated escalations" in message