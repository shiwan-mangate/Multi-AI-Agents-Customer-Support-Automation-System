import pytest
from unittest.mock import MagicMock

from crm_agent.services.customer.profile_service import ProfileService

# =========================================================
# Fixtures
# =========================================================

@pytest.fixture
def profile_service():
    """Provides a ProfileService with a mocked repository."""
    mock_repo = MagicMock()
    return ProfileService(profile_repo=mock_repo)

@pytest.fixture
def valid_event():
    """Provides a mocked event that passes all service validations."""
    event = MagicMock()
    event.customer.customer_id = 10592
    event.event.source_agent = "refund_agent"
    event.resolution.status = "resolved"
    return event

# =========================================================
# Validation Tests
# =========================================================

def test_missing_customer_id(profile_service, valid_event):
    valid_event.customer.customer_id = None
    
    with pytest.raises(ValueError, match=r"customer_id is required\."):
        profile_service.update_customer_profile(valid_event)
        
    # Ensure repo is NEVER called if validation fails
    profile_service.profile_repo.upsert_profile_from_event.assert_not_called()

def test_missing_source_agent(profile_service, valid_event):
    valid_event.event.source_agent = None
    
    with pytest.raises(ValueError, match=r"source_agent is required\."):
        profile_service.update_customer_profile(valid_event)
        
    profile_service.profile_repo.upsert_profile_from_event.assert_not_called()

def test_missing_resolution_status(profile_service, valid_event):
    valid_event.resolution.status = None
    
    with pytest.raises(ValueError, match=r"resolution status is required\."):
        profile_service.update_customer_profile(valid_event)
        
    profile_service.profile_repo.upsert_profile_from_event.assert_not_called()

# =========================================================
# Execution Tests
# =========================================================

def test_successful_profile_update(profile_service, valid_event):
    # Execute the service
    profile_service.update_customer_profile(valid_event)
    
    # Verify it correctly delegated to the repository exactly once
    profile_service.profile_repo.upsert_profile_from_event.assert_called_once_with(valid_event)

def test_repository_failure_propagates(profile_service, valid_event):
    # Simulate a database failure in the repository
    profile_service.profile_repo.upsert_profile_from_event.side_effect = Exception("Database timeout")
    
    # Ensure the service doesn't swallow the error
    with pytest.raises(Exception, match="Database timeout"):
        profile_service.update_customer_profile(valid_event)