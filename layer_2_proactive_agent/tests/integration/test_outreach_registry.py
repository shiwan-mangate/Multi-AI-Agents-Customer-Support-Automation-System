import os
import pytest
from datetime import datetime, timedelta, UTC
from uuid import uuid4

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from layer_2_proactive_agent.repositories.proactive_outreach_repository import (
    ProactiveOutreachRepository,
)
from layer_2_proactive_agent.services.suppression_service import (
    SuppressionService,
)

from layer_2_proactive_agent.database.base import Base  
from layer_2_proactive_agent.database.model.proactive_outreach_record import (
    ProactiveOutreachRecord,
)
from layer_2_proactive_agent.schemas.enums import SignalType, OutreachStatus


# ==============================================================================
# DATABASE FIXTURES (IN-MEMORY SQLITE FOR FAST TESTING)
# ==============================================================================

@pytest.fixture(scope="module")
def db_engine():
    # Use an in-memory SQLite database for blazing fast, isolated testing
    db_url = "sqlite:///:memory:"
    
    engine = create_engine(db_url)
    Base.metadata.create_all(engine)
    
    yield engine
    
    Base.metadata.drop_all(engine)


@pytest.fixture
def db_session(db_engine):
    Session = sessionmaker(bind=db_engine)
    session = Session()
    yield session
    session.rollback()
    session.close()


@pytest.fixture
def suppression_service(db_session):
    """
    Instantiates the full domain boundary: Service + Repository.
    """
    repo = ProactiveOutreachRepository(session=db_session)
    return SuppressionService(repo=repo)


# ==============================================================================
# INTEGRATION TESTS: SUPPRESSION SERVICE + REPOSITORY
# ==============================================================================

def test_full_outreach_lifecycle_and_suppression(suppression_service, db_session):
    """
    Integration test: Proves that saving an outreach record correctly 
    blocks subsequent outreach attempts for the configured window.
    """
    customer_id = 1001
    signal_type = SignalType.HIGH_CHURN_RISK
    workflow_id = f"WF-{uuid4().hex[:6]}"
    signal_id = f"SIG-{uuid4().hex[:6]}"

    # 1. Verify initial state (Customer should NOT be suppressed)
    is_suppressed, record_id = suppression_service.should_suppress(
        customer_id=customer_id, 
        signal_type=signal_type
    )
    assert is_suppressed is False
    assert record_id is None

    # 2. Create and Save Outreach
    record = suppression_service.create_outreach_record(
        workflow_id=workflow_id,
        signal_id=signal_id,
        customer_id=customer_id,
        signal_type=signal_type,
        decision="OUTREACH_EXECUTED"
    )
    suppression_service.save_outreach(record)
    db_session.commit()

    # 3. Verify Database Persistence & Expiry Math
    saved_record = db_session.get(ProactiveOutreachRecord, record.id)
    assert saved_record is not None
    assert saved_record.status == OutreachStatus.OUTREACH_CREATED.value
    
    # FIX: SQLite drops timezone awareness. We explicitly cast it back to UTC 
    # so we can do math against our timezone-aware expected_expiry.
    db_expiry_utc = saved_record.expires_at.replace(tzinfo=UTC)
    expected_expiry = datetime.now(UTC) + timedelta(days=14)
    
    time_diff = abs((db_expiry_utc - expected_expiry).total_seconds())
    assert time_diff < 5.0  # Allow up to 5 seconds of execution time drift

    # 4. Verify Suppression Gate is now CLOSED
    is_suppressed, active_record_id = suppression_service.should_suppress(
        customer_id=customer_id, 
        signal_type=signal_type
    )
    assert is_suppressed is True
    assert active_record_id == record.id


def test_expired_records_allow_new_outreach(suppression_service, db_session):
    """
    Integration test: Proves that the repository ignores records where 
    expires_at is in the past, allowing the service to approve new outreach.
    """
    customer_id = 1002
    signal_type = SignalType.INACTIVE_CUSTOMER

    # 1. Manually insert an EXPIRED record
    expired_record = ProactiveOutreachRecord(
        id=str(uuid4()),
        workflow_id="WF-OLD",
        signal_id="SIG-OLD",
        customer_id=customer_id,
        signal_type=signal_type.value,
        decision="OUTREACH_EXECUTED",
        status=OutreachStatus.OUTREACH_CREATED.value,
        created_at=datetime.now(UTC) - timedelta(days=40),
        expires_at=datetime.now(UTC) - timedelta(days=10) # Expired 10 days ago
    )
    db_session.add(expired_record)
    db_session.commit()

    # 2. Verify Suppression Gate is OPEN
    is_suppressed, record_id = suppression_service.should_suppress(
        customer_id=customer_id, 
        signal_type=signal_type
    )
    
    assert is_suppressed is False
    assert record_id is None


def test_cross_signal_suppression_isolation(suppression_service, db_session):
    """
    Integration test: Proves that a suppression record for one SignalType 
    does not accidentally suppress a different SignalType for the same customer.
    """
    customer_id = 1003
    
    # 1. Suppress the customer for VIP_RETENTION_RISK
    record = suppression_service.create_suppression_record(
        workflow_id="WF-VIP",
        signal_id="SIG-VIP",
        customer_id=customer_id,
        signal_type=SignalType.VIP_RETENTION_RISK
    )
    suppression_service.save_suppression(record)
    db_session.commit()

    # 2. Verify VIP is suppressed
    is_suppressed_vip, _ = suppression_service.should_suppress(
        customer_id=customer_id, 
        signal_type=SignalType.VIP_RETENTION_RISK
    )
    assert is_suppressed_vip is True

    # 3. Verify CHURN is NOT suppressed
    is_suppressed_churn, _ = suppression_service.should_suppress(
        customer_id=customer_id, 
        signal_type=SignalType.HIGH_CHURN_RISK
    )
    assert is_suppressed_churn is False


def test_expiry_window_calculations(suppression_service):
    """
    Verifies the domain rules for suppression durations map exactly 
    to the expected datetime deltas without requiring DB insertion.
    """
    now = datetime.now(UTC)
    
    # Check 30 day window
    inactive_expiry = suppression_service.calculate_expiry(SignalType.INACTIVE_CUSTOMER)
    assert abs((inactive_expiry - (now + timedelta(days=30))).total_seconds()) < 5.0
    
    # Check 7 day window
    vip_expiry = suppression_service.calculate_expiry(SignalType.VIP_RETENTION_RISK)
    assert abs((vip_expiry - (now + timedelta(days=7))).total_seconds()) < 5.0


def test_cleanup_expired_records(suppression_service, db_session):
    """
    Integration test: Verifies that the cleanup job accurately deletes records 
    older than the retention cutoff (e.g. 90 days), while keeping active 
    and recently expired records.
    """
    repo = suppression_service.repo
    
    # 1. Very old expired record (Should be deleted: > 90 days ago)
    old_record = ProactiveOutreachRecord(
        id=str(uuid4()),
        workflow_id="WF-1",
        signal_id="SIG-1",
        customer_id=1,
        signal_type=SignalType.HIGH_CHURN_RISK.value,
        decision="OUTREACH",
        status=OutreachStatus.OUTREACH_CREATED.value,
        created_at=datetime.now(UTC) - timedelta(days=120),
        expires_at=datetime.now(UTC) - timedelta(days=106)
    )
    
    # 2. Recently expired record (Should be KEPT: Expired, but < 90 days ago)
    recent_record = ProactiveOutreachRecord(
        id=str(uuid4()),
        workflow_id="WF-2",
        signal_id="SIG-2",
        customer_id=2,
        signal_type=SignalType.HIGH_CHURN_RISK.value,
        decision="OUTREACH",
        status=OutreachStatus.OUTREACH_CREATED.value,
        created_at=datetime.now(UTC) - timedelta(days=40),
        expires_at=datetime.now(UTC) - timedelta(days=26)
    )
    
    # FIX: Extract the raw string IDs BEFORE committing to the DB, 
    # so we don't try to access deleted SQLAlchemy objects later.
    old_record_id_str = old_record.id
    recent_record_id_str = recent_record.id

    db_session.add_all([old_record, recent_record])
    db_session.commit()

    # Act - Run cleanup for anything expiring more than 90 days ago
    deleted_count = repo.cleanup_expired_records(retention_days=90)
    db_session.commit()

    # Assert that at least our old record was deleted
    assert deleted_count >= 1
    
    # Assert using ID-isolation to prevent shared table flakiness
    remaining_ids = {r.id for r in db_session.query(ProactiveOutreachRecord).all()}
    
    assert old_record_id_str not in remaining_ids
    assert recent_record_id_str in remaining_ids