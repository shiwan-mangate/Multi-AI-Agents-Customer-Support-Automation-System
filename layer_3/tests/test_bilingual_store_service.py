import sys
import os

# Dynamically add layer_3 to the Python path
layer_3_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if layer_3_path not in sys.path:
    sys.path.insert(0, layer_3_path)

import pytest
from unittest.mock import MagicMock

from layer_3.storage.bilingual_store_service import BilingualStoreService
from layer_3.schemas.bilingual_message import BilingualMessage, LanguageContext
from layer_3.schemas.translation_record import TranslationRecord

class TestBilingualStoreService:

    @pytest.fixture
    def mock_repo(self):
        """Yields a mocked TranslationRepository."""
        repo = MagicMock()
        # Default to no existing translation to allow the happy path
        repo.translation_exists.return_value = False
        return repo

    @pytest.fixture
    def service(self, mock_repo):
        """Yields the BilingualStoreService injected with the mock repo."""
        return BilingualStoreService(repository=mock_repo)

    @pytest.fixture
    def sample_message(self):
        """Yields a standard inbound BilingualMessage."""
        return BilingualMessage(
            original_text="मुझे रिफंड चाहिए",
            english_text="I want a refund",
            language_context=LanguageContext(
                detected_language="hi",
                detection_confidence=0.99,
                detection_method="fast_text",
                translation_used=True,
                translation_failed=False,
                fallback_triggered=False,
                mixed_language_detected=False,
                script_detected=None
            )
        )

    # 1. Happy Path
    def test_store_inbound_message_success(self, service, mock_repo, sample_message):
        result = service.store_inbound_message("TKT-001", 123, sample_message)
        
        assert result.ticket_id == "TKT-001"
        assert result.customer_id == 123
        assert result.original_text == "मुझे रिफंड चाहिए"
        assert result.english_text == "I want a refund"
        
        mock_repo.translation_exists.assert_called_once_with("TKT-001")
        mock_repo.create_record.assert_called_once()

    # 2. Translation Failure Mapping
    def test_store_translation_failure_record(self, service, mock_repo, sample_message):
        # Mutate the fixture to simulate a failed translation
        sample_message.language_context.translation_failed = True
        
        result = service.store_inbound_message("TKT-002", 123, sample_message)
        
        assert result.translation_success is False
        mock_repo.create_record.assert_called_once()

    # 3. Idempotency (Skip Duplicate)
    def test_skip_duplicate_translation(self, service, mock_repo, sample_message):
        # Simulate a database where this ticket is already stored
        mock_repo.translation_exists.return_value = True
        
        result = service.store_inbound_message("TKT-003", 123, sample_message)
        
        # Verify persistence was bypassed but the domain record is still returned
        mock_repo.create_record.assert_not_called()
        assert result.ticket_id == "TKT-003" 

    # 4. Exception Propagation
    def test_repository_failure_raises_exception(self, service, mock_repo, sample_message):
        # Simulate a database outage
        mock_repo.create_record.side_effect = Exception("DB Down")
        
        with pytest.raises(Exception, match="DB Down"):
            service.store_inbound_message("TKT-004", 123, sample_message)
            
        mock_repo.create_record.assert_called_once()

    # 5. Type Consistency
    def test_customer_id_remains_integer(self, service, mock_repo, sample_message):
        result = service.store_inbound_message("TKT-005", 999, sample_message)
        
        assert isinstance(result.customer_id, int)
        assert result.customer_id == 999

    # 6. Service Constant Mapping
    def test_translation_service_set(self, service, mock_repo, sample_message):
        result = service.store_inbound_message("TKT-006", 123, sample_message)
        assert result.translation_service == "helsinki"

    # 7. Domain Contract Adherence
    def test_repository_receives_translation_record(self, service, mock_repo, sample_message):
        service.store_inbound_message("TKT-007", 123, sample_message)
        
        # Extract the exact argument passed to create_record
        args, _ = mock_repo.create_record.call_args
        
        # Verify it's the exact Pydantic domain model, not a raw dict
        assert isinstance(args[0], TranslationRecord)