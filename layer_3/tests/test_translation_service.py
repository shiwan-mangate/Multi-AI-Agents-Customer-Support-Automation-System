import sys
import os
from pathlib import Path

# ---------------------------------------------------------
# PATH ROUTING FIX
# ---------------------------------------------------------
current_dir = Path(__file__).parent.resolve()
layer_3_dir = current_dir.parent.resolve()
root_dir = layer_3_dir.parent.resolve()

if str(layer_3_dir) not in sys.path:
    sys.path.insert(0, str(layer_3_dir))
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

import pytest
from unittest.mock import Mock, patch

from layer_3.service.translation_service import TranslationService
from layer_3.schemas.inbound_translation_response import InboundTranslationResponse
from layer_3.schemas.translation_result import TranslationResult
from layer_3.schemas.bilingual_message import BilingualMessage, LanguageContext
from layer_3.schemas.translation_record import TranslationRecord
from layer_3.schemas.translation_persistence_event import TranslationPersistenceEvent

class TestTranslationService:

    @pytest.fixture
    def mock_repo(self):
        """Yields a mocked repository."""
        return Mock()

    @pytest.fixture
    def service(self, mock_repo):
        """
        Yields a TranslationService with its internal pipelines explicitly patched.
        This prevents the InboundPipeline from trying to physically load fastText 
        ML models from the disk during unit testing.
        """
        # Updated patch paths to match the 'service.' module namespace
        with patch('service.translation_service.InboundTranslationPipeline'), \
             patch('service.translation_service.OutboundTranslationPipeline'), \
             patch('service.translation_service.BilingualStoreService'), \
             patch('service.translation_service.TranslationPersistenceService'), \
             patch('service.translation_service.TranslationAnalyticsService'):
             
            svc = TranslationService(repository=mock_repo)
            yield svc

    # ---------------------------------------------------------
    # 1. Constructor Wiring
    # ---------------------------------------------------------
    def test_constructor_wiring(self, service, mock_repo):
        """Verifies the Facade instantiates all its required dependencies."""
        assert service.repository == mock_repo
        assert service.inbound_pipeline is not None
        assert service.outbound_pipeline is not None
        assert service.store_service is not None
        assert service.persistence_service is not None
        assert service.analytics_service is not None

    # ---------------------------------------------------------
    # 2. Inbound Orchestration Tests
    # ---------------------------------------------------------
    def test_process_inbound_message_success(self, service):
        # Mocks
        mock_bilingual = Mock(spec=BilingualMessage)
        mock_bilingual.language_context = Mock(spec=LanguageContext, detected_language="hi")
        mock_record = Mock(spec=TranslationRecord)
        mock_event = Mock(spec=TranslationPersistenceEvent)
        
        service.inbound_pipeline.process_inbound.return_value = mock_bilingual
        service.store_service.store_inbound_message.return_value = mock_record
        service.persistence_service.create_persistence_event.return_value = mock_event

        # Execute
        response = service.process_inbound_message(
            ticket_id="TKT-001",
            customer_id=123,
            message="नमस्ते",
            customer_context={"vip": True}
        )

        # Verify Execution Flow
        service.inbound_pipeline.process_inbound.assert_called_once_with(
            text="नमस्ते", customer_context={"vip": True}
        )
        service.store_service.store_inbound_message.assert_called_once_with(
            ticket_id="TKT-001", customer_id=123, bilingual_message=mock_bilingual
        )
        service.persistence_service.create_persistence_event.assert_called_once_with(
            translation_record=mock_record
        )

        # Verify Contract Return
        assert isinstance(response, InboundTranslationResponse)
        assert response.bilingual_message == mock_bilingual
        assert response.translation_record == mock_record
        assert response.persistence_event == mock_event

    def test_process_inbound_message_translation_failed(self, service):
            # Mocks
            mock_bilingual = Mock(spec=BilingualMessage)
            mock_bilingual.language_context = Mock(spec=LanguageContext, detected_language="unknown")
            
            service.inbound_pipeline.process_inbound.return_value = mock_bilingual
            
            # FIX: Explicitly cast the specs so Pydantic accepts the mocks
            service.store_service.store_inbound_message.return_value = Mock(spec=TranslationRecord)
            service.persistence_service.create_persistence_event.return_value = Mock(spec=TranslationPersistenceEvent)

            # Execute
            response = service.process_inbound_message("TKT-002", 123, "???")

            # Verify orchestrator still passes data through without crashing
            assert isinstance(response, InboundTranslationResponse)
            service.store_service.store_inbound_message.assert_called_once()

    def test_process_inbound_message_store_service_failure(self, service):
        # Mocks
        service.inbound_pipeline.process_inbound.return_value = Mock(spec=BilingualMessage)
        service.store_service.store_inbound_message.side_effect = Exception("Database Down")

        # Execute & Verify
        with pytest.raises(Exception, match="Database Down"):
            service.process_inbound_message("TKT-003", 123, "Hello")

        # Verify event creation was skipped due to exception
        service.persistence_service.create_persistence_event.assert_not_called()

    # ---------------------------------------------------------
    # 3. Outbound Orchestration Tests
    # ---------------------------------------------------------
    def test_process_outbound_response_success(self, service):
        # Mocks
        mock_result = TranslationResult(
            translated_text="Hola",
            source_language="en",
            target_language="es",
            translation_service="helsinki",
            translation_success=True
        )
        service.outbound_pipeline.process_outbound.return_value = mock_result

        # Execute
        result = service.process_outbound_response(
            ticket_id="TKT-004",
            english_response="Hello",
            target_language="es",
            source_agent="refund_agent"
        )

        # Verify Execution
        service.outbound_pipeline.process_outbound.assert_called_once_with(
            english_response="Hello", target_language="es", source_agent="refund_agent"
        )
        
        # Verify DB Update Occurred (Because success=True)
        service.persistence_service.persist_outbound_translation.assert_called_once_with(
            ticket_id="TKT-004",
            response_english="Hello",
            response_translated="Hola",
            response_language="es"
        )
        assert result == mock_result

    def test_process_outbound_response_failed_translation(self, service):
        # Mocks (Simulating a hallucination or failure)
        mock_result = TranslationResult(
            translated_text="Hello", # Fallback to English
            source_language="en",
            target_language="es",
            translation_service="helsinki",
            translation_success=False
        )
        service.outbound_pipeline.process_outbound.return_value = mock_result

        # Execute
        result = service.process_outbound_response("TKT-005", "Hello", "es")

        # Verify DB Update was SKIPPED due to failure guard
        service.persistence_service.persist_outbound_translation.assert_not_called()
        assert result.translation_success is False

    def test_process_outbound_response_pipeline_exception(self, service):
        service.outbound_pipeline.process_outbound.side_effect = Exception("Model Offline")

        with pytest.raises(Exception, match="Model Offline"):
            service.process_outbound_response("TKT-006", "Hello", "hi")

        service.persistence_service.persist_outbound_translation.assert_not_called()

    # ---------------------------------------------------------
    # 4. Analytics Orchestration
    # ---------------------------------------------------------
    def test_get_customer_language_profile_success(self, service):
        expected_profile = {"preferred_language": "hi", "dominance_score": 0.85}
        service.analytics_service.get_customer_language_profile.return_value = expected_profile

        result = service.get_customer_language_profile(123)

        service.analytics_service.get_customer_language_profile.assert_called_once_with(123)
        assert result == expected_profile