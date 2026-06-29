# tests/unit/test_event_claiming.py

import pytest
from unittest.mock import MagicMock

from crm_agent.services.ingestion.event_claim_service import EventClaimService
from crm_agent.repositories.customer_event_repository import CRMEventRepository


# =========================================================
# Fixtures
# =========================================================
@pytest.fixture
def event_claim_service():
    """Injects a MagicMock repository and session into the claim service."""
    # Using spec guarantees we don't mock non-existent repository methods
    mock_repo = MagicMock(spec=CRMEventRepository)
    mock_repo.session = MagicMock()
    return EventClaimService(event_repo=mock_repo)


# =========================================================
# 1. Claiming Events
# =========================================================
def test_claim_success(event_claim_service):
    fake_event_1 = MagicMock()
    fake_event_2 = MagicMock()
    event_claim_service.event_repo.claim_events_for_processing.return_value = [
        fake_event_1,
        fake_event_2
    ]

    events = event_claim_service.claim_events(
        worker_id="worker_1",
        batch_size=5
    )

    assert len(events) == 2
    event_claim_service.event_repo.claim_events_for_processing.assert_called_once_with(
        worker_id="worker_1",
        batch_size=5
    )


def test_claim_empty_queue(event_claim_service):
    event_claim_service.event_repo.claim_events_for_processing.return_value = []

    events = event_claim_service.claim_events(worker_id="worker_2")

    assert events == []
    # Explicitly verify the default batch_size parameter is passed correctly
    event_claim_service.event_repo.claim_events_for_processing.assert_called_once_with(
        worker_id="worker_2",
        batch_size=5
    )


def test_claim_repository_failure(event_claim_service):
    event_claim_service.event_repo.claim_events_for_processing.side_effect = Exception("DB Timeout")

    with pytest.raises(Exception, match="DB Timeout"):
        event_claim_service.claim_events(worker_id="worker_3")


# =========================================================
# 2. Releasing Stale Claims & Dead-Lettering
# =========================================================
def test_release_stale_claims_success(event_claim_service):
    fake_result = MagicMock()
    fake_result.rowcount = 3
    event_claim_service.event_repo.session.execute.return_value = fake_result

    count = event_claim_service.release_stale_claims()

    assert count == 3
    event_claim_service.event_repo.session.commit.assert_called_once()
    event_claim_service.event_repo.session.rollback.assert_not_called()


def test_release_stale_claims_zero(event_claim_service):
    fake_result = MagicMock()
    fake_result.rowcount = 0
    event_claim_service.event_repo.session.execute.return_value = fake_result

    count = event_claim_service.release_stale_claims()

    assert count == 0
    event_claim_service.event_repo.session.commit.assert_called_once()


def test_release_stale_claims_none_rowcount(event_claim_service):
    # Verify the `rowcount or 0` fallback logic for specific SQL drivers
    fake_result = MagicMock()
    fake_result.rowcount = None
    event_claim_service.event_repo.session.execute.return_value = fake_result

    count = event_claim_service.release_stale_claims()

    assert count == 0
    event_claim_service.event_repo.session.commit.assert_called_once()


def test_release_stale_claims_executes_dead_letter_query(event_claim_service):
    fake_result = MagicMock()
    fake_result.rowcount = 1
    event_claim_service.event_repo.session.execute.return_value = fake_result

    event_claim_service.release_stale_claims()

    # Verify both stale recovery and dead-letter query execute
    assert event_claim_service.event_repo.session.execute.call_count == 2


def test_release_stale_claims_rollback_on_failure(event_claim_service):
    event_claim_service.event_repo.session.execute.side_effect = Exception("Deadlock detected")

    with pytest.raises(Exception, match="Deadlock detected"):
        event_claim_service.release_stale_claims()

    event_claim_service.event_repo.session.rollback.assert_called_once()
    event_claim_service.event_repo.session.commit.assert_not_called()


def test_release_stale_claims_custom_timeout(event_claim_service):
    fake_result = MagicMock()
    fake_result.rowcount = 0
    event_claim_service.event_repo.session.execute.return_value = fake_result

    event_claim_service.release_stale_claims(
        timeout_minutes=30,
        max_retries=5
    )

    assert event_claim_service.event_repo.session.execute.call_count == 2
    event_claim_service.event_repo.session.commit.assert_called_once()