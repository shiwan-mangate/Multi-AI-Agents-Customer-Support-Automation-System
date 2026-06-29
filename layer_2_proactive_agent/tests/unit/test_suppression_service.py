import pytest
from unittest.mock import Mock
from datetime import datetime, UTC

from layer_2_proactive_agent.services.suppression_service import (
    SuppressionService,
    SUPPRESSION_WINDOWS,
)

from layer_2_proactive_agent.database.model.proactive_outreach_record import (
    ProactiveOutreachRecord,
)

from layer_2_proactive_agent.schemas.enums import (
    SignalType,
    OutreachStatus,
)


@pytest.fixture
def mock_repo():
    """Provides a mocked repository to intercept database calls."""
    return Mock()


@pytest.fixture
def service(mock_repo):
    """Provides a fresh SuppressionService instance with a mocked repo."""
    return SuppressionService(repo=mock_repo)


# ---------------------------------------------------------
# Test 1 & 2: Suppression Check Logic
# ---------------------------------------------------------

def test_should_suppress_returns_true_when_record_exists(
    service, 
    mock_repo,
):
    """
    If the repository finds a recent contact record, the service 
    must return True and the exact ID of the blocking record.
    """
    
    mock_record = Mock()
    mock_record.id = "REC-999"
    mock_repo.already_contacted.return_value = mock_record

    customer_id = 123
    signal_type = SignalType.HIGH_CHURN_RISK

    suppressed, record_id = service.should_suppress(
        customer_id=customer_id,
        signal_type=signal_type,
    )

    mock_repo.already_contacted.assert_called_once_with(
        customer_id=customer_id,
        signal_type=signal_type.value,
    )
    
    assert suppressed is True
    assert record_id == "REC-999"


def test_should_suppress_returns_false_when_no_record(
    service, 
    mock_repo,
):
    """
    If the repository returns None, the service must return 
    False and None, allowing the workflow to proceed.
    """
    
    mock_repo.already_contacted.return_value = None

    suppressed, record_id = service.should_suppress(
        customer_id=456,
        signal_type=SignalType.VIP_RETENTION_RISK,
    )

    assert suppressed is False
    assert record_id is None


# ---------------------------------------------------------
# Test 3: Expiry Date Math Matrix
# ---------------------------------------------------------

@pytest.mark.parametrize(
    "signal_type, expected_days",
    [
        (SignalType.INACTIVE_CUSTOMER, 30),
        (SignalType.HIGH_CHURN_RISK, 14),
        (SignalType.RECENT_NEGATIVE_EXPERIENCE, 14),
        (SignalType.VIP_RETENTION_RISK, 7),
    ]
)
def test_calculate_expiry_windows(
    service,
    signal_type,
    expected_days,
):
    """
    Exhaustively verifies that the correct timedelta is applied 
    based on the exact signal type using the SUPPRESSION_WINDOWS mapping.
    """
    
    expiry = service.calculate_expiry(signal_type=signal_type)

    now = datetime.now(UTC)
    delta = expiry - now
    
    expected_seconds = expected_days * 86400
    assert abs(delta.total_seconds() - expected_seconds) < 5 


# ---------------------------------------------------------
# Test 4: Record Creation Mappings
# ---------------------------------------------------------

def test_create_outreach_record_mapping(
    service,
):
    """
    Verifies the factory method correctly constructs a DB record 
    for an active outreach decision.
    """
    
    workflow_id = "WF-001"
    signal_id = "SIG-123"
    customer_id = 999
    signal_type = SignalType.HIGH_CHURN_RISK
    decision = "Proactive email regarding low usage."

    record = service.create_outreach_record(
        workflow_id=workflow_id,
        signal_id=signal_id,
        customer_id=customer_id,
        signal_type=signal_type,
        decision=decision,
    )

    assert isinstance(record, ProactiveOutreachRecord)
    assert record.workflow_id == workflow_id
    assert record.signal_id == signal_id
    assert record.customer_id == customer_id
    
    assert record.signal_type == signal_type.value
    assert record.status == OutreachStatus.OUTREACH_CREATED.value
    
    assert record.decision == decision
    assert isinstance(record.expires_at, datetime)


def test_create_suppression_record_mapping(
    service,
):
    """
    Verifies the factory method correctly constructs a DB record 
    specifically earmarked as suppressed (early exit).
    """
    
    record = service.create_suppression_record(
        workflow_id="WF-SUPP",
        signal_id="SIG-404",
        customer_id=888,
        signal_type=SignalType.INACTIVE_CUSTOMER,
    )

    assert isinstance(record, ProactiveOutreachRecord)
    assert record.workflow_id == "WF-SUPP"
    assert record.decision == "SUPPRESSED"
    assert record.status == OutreachStatus.SUPPRESSED.value
    assert isinstance(record.expires_at, datetime)


# ---------------------------------------------------------
# Test 5: Repository Delegation (Save operations)
# ---------------------------------------------------------

def test_save_outreach_delegation(
    service,
    mock_repo,
):
    """
    Ensures saving an outreach record correctly delegates 
    to the repository's dedicated outreach insert method.
    """
    
    mock_record = Mock(spec=ProactiveOutreachRecord)
    mock_repo.record_outreach.return_value = mock_record

    result = service.save_outreach(record=mock_record)

    mock_repo.record_outreach.assert_called_once_with(mock_record)
    assert result == mock_record


def test_save_suppression_delegation(
    service,
    mock_repo,
):
    """
    Ensures saving a suppression record correctly delegates 
    to the repository's dedicated suppression insert method.
    """
    
    mock_record = Mock(spec=ProactiveOutreachRecord)
    mock_repo.record_suppression.return_value = mock_record

    result = service.save_suppression(record=mock_record)

    mock_repo.record_suppression.assert_called_once_with(mock_record)
    assert result == mock_record


# ---------------------------------------------------------
# Test 6: Repository Exception Propagation
# ---------------------------------------------------------

def test_should_suppress_repository_failure(
    service,
    mock_repo,
):
    """
    Database/repository exceptions must propagate 
    and not be swallowed by the service layer.
    """

    mock_repo.already_contacted.side_effect = Exception(
        "Database unavailable"
    )

    with pytest.raises(
        Exception,
        match="Database unavailable"
    ):
        service.should_suppress(
            customer_id=123,
            signal_type=SignalType.HIGH_CHURN_RISK,
        )


# ---------------------------------------------------------
# Test 7: Verify Suppression Window Configuration
# ---------------------------------------------------------

def test_suppression_windows_configuration():
    """
    Protect business suppression policies from accidental 
    changes by pinning the explicit integer values.
    """

    assert SUPPRESSION_WINDOWS[SignalType.INACTIVE_CUSTOMER] == 30
    assert SUPPRESSION_WINDOWS[SignalType.HIGH_CHURN_RISK] == 14
    assert SUPPRESSION_WINDOWS[SignalType.RECENT_NEGATIVE_EXPERIENCE] == 14
    assert SUPPRESSION_WINDOWS[SignalType.VIP_RETENTION_RISK] == 7