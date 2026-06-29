import sys
import os

layer_3_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if layer_3_path not in sys.path:
    sys.path.insert(0, layer_3_path)

import pytest
from unittest.mock import MagicMock

from layer_3.storage.translation_persistence_service import TranslationPersistenceService
from layer_3.schemas.translation_record import TranslationRecord
from layer_3.schemas.translation_persistence_event import TranslationPersistenceEvent

class TestTranslationPersistenceService:

    @pytest.fixture
    def mock_repo(self):
        """Yields a mocked TranslationRepository."""
        return MagicMock()

    @pytest.fixture
    def service(self, mock_repo):
        """Yields the TranslationPersistenceService injected with the mock repo."""
        return TranslationPersistenceService(repository=mock_repo)

    @pytest.fixture
    def translation_record(self):
        """Yields a standard inbound TranslationRecord domain model."""
        return TranslationRecord(
            ticket_id="TKT-1001",
            customer_id=123,
            original_text="मुझे रिफंड चाहिए",
            original_language="hi",
            english_text="I need a refund",
            translation_service="helsinki",
            translation_success=True
        )


    
    def test_create_persistence_event_success(self, service, translation_record):
        event = service.create_persistence_event(translation_record)
        
        assert event.ticket_id == "TKT-1001"
        assert event.customer_id == 123
        assert event.processing_status == "PENDING"
        assert event.source_system == "inbound_pipeline"
        assert event.translation_record == translation_record

    def test_create_event_custom_source_system(self, service, translation_record):
        event = service.create_persistence_event(translation_record, source_system="faq_agent")
        
        assert event.source_system == "faq_agent"

    def test_event_id_generated(self, service, translation_record):
        event = service.create_persistence_event(translation_record)
        
        assert event.event_id.startswith("evt_")
        assert len(event.event_id) > 10
        assert event.created_at is not None



    def test_persist_outbound_translation_success(self, service, mock_repo):
       
        mock_repo.translation_exists.return_value = True
        mock_repo.update_outbound_translation.return_value = True
        
        result = service.persist_outbound_translation(
            ticket_id="TKT-1001",
            response_english="Refund approved",
            response_translated="रिफंड स्वीकृत",
            response_language="hi"
        )
        
        assert result is True
        mock_repo.translation_exists.assert_called_once_with("TKT-1001")
        mock_repo.update_outbound_translation.assert_called_once()

    def test_persist_outbound_translation_record_not_found(self, service, mock_repo):
       
        mock_repo.translation_exists.return_value = False
        
        result = service.persist_outbound_translation(
            ticket_id="TKT-1001",
            response_english="Refund approved",
            response_translated="रिफंड स्वीकृत",
            response_language="hi"
        )
        
        assert result is False
        mock_repo.update_outbound_translation.assert_not_called()

    def test_persist_outbound_translation_update_failed(self, service, mock_repo):
        # Setup Repository returning False
        mock_repo.translation_exists.return_value = True
        mock_repo.update_outbound_translation.return_value = False
        
        result = service.persist_outbound_translation(
            ticket_id="TKT-1001",
            response_english="Refund approved",
            response_translated="रिफंड स्वीकृत",
            response_language="hi"
        )
        
        assert result is False

    def test_persist_outbound_translation_exception(self, service, mock_repo):
       
        mock_repo.translation_exists.return_value = True
        mock_repo.update_outbound_translation.side_effect = Exception("Database unavailable")
        
        result = service.persist_outbound_translation(
            ticket_id="TKT-1001",
            response_english="Refund approved",
            response_translated="रिफंड स्वीकृत",
            response_language="hi"
        )
        
      
        assert result is False

    def test_outbound_translation_parameters(self, service, mock_repo):
        mock_repo.translation_exists.return_value = True
        mock_repo.update_outbound_translation.return_value = True
        
        service.persist_outbound_translation(
            ticket_id="TKT-1001",
            response_english="Refund approved",
            response_translated="रिफंड स्वीकृत",
            response_language="hi"
        )
        
        mock_repo.update_outbound_translation.assert_called_once_with(
            ticket_id="TKT-1001",
            response_english="Refund approved",
            response_translated="रिफंड स्वीकृत",
            response_language="hi"
        )