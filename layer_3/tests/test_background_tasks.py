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
from unittest.mock import Mock

from layer_3.service.background_tasks import BackgroundTasksService
from layer_3.schemas.bilingual_message import BilingualMessage, LanguageContext
from layer_3.schemas.translation_record import TranslationRecord
from layer_3.schemas.translation_persistence_event import TranslationPersistenceEvent

# ==========================================================
# Test Helpers
# ==========================================================

def build_bilingual_message():
    return BilingualMessage(
        original_text="नमस्ते",
        english_text="hello",
        language_context=LanguageContext(
            detected_language="hi",
            detection_confidence=0.99,
            detection_method="script_fast_path",
            translation_used=True,
            translation_failed=False,
            fallback_triggered=False,
            mixed_language_detected=False
        )
    )

def build_translation_record():
    return TranslationRecord(
        ticket_id="TKT-100",
        customer_id=1,
        original_text="नमस्ते",
        original_language="hi",
        english_text="hello",
        translation_service="helsinki",
        translation_success=True
    )

def build_persistence_event():
    return TranslationPersistenceEvent(
        ticket_id="TKT-100",
        customer_id=1,
        translation_record=build_translation_record(),
        source_system="inbound_pipeline",
        processing_status="PENDING"
    )

class TestBackgroundTasksService:

    # ==========================================================
    # persist_inbound_translation
    # ==========================================================

    def test_persist_inbound_translation_success(self):
        store_service = Mock()
        persistence_service = Mock()

        record = build_translation_record()
        event = build_persistence_event()

        store_service.store_inbound_message.return_value = record
        persistence_service.create_persistence_event.return_value = event

        service = BackgroundTasksService(store_service, persistence_service)
        service.dispatch_translation_event = Mock(return_value=True)

        result = service.persist_inbound_translation(
            ticket_id="TKT-100",
            customer_id=1,
            bilingual_message=build_bilingual_message()
        )

        assert result is True
        store_service.store_inbound_message.assert_called_once()
        persistence_service.create_persistence_event.assert_called_once_with(translation_record=record)
        service.dispatch_translation_event.assert_called_once_with(event)

    def test_persist_inbound_translation_store_failure(self):
        store_service = Mock()
        persistence_service = Mock()

        store_service.store_inbound_message.side_effect = Exception("database failure")

        service = BackgroundTasksService(store_service, persistence_service)
        service.dispatch_translation_event = Mock()

        # Should NOT raise, should return False
        result = service.persist_inbound_translation(
            ticket_id="TKT-100",
            customer_id=1,
            bilingual_message=build_bilingual_message()
        )

        assert result is False
        service.dispatch_translation_event.assert_not_called()

    def test_persist_inbound_translation_event_creation_failure(self):
        store_service = Mock()
        persistence_service = Mock()

        store_service.store_inbound_message.return_value = build_translation_record()
        persistence_service.create_persistence_event.side_effect = Exception("event failure")

        service = BackgroundTasksService(store_service, persistence_service)
        service.dispatch_translation_event = Mock()

        # Should NOT raise, should return False
        result = service.persist_inbound_translation(
            ticket_id="TKT-100",
            customer_id=1,
            bilingual_message=build_bilingual_message()
        )

        assert result is False
        service.dispatch_translation_event.assert_not_called()

    def test_persist_inbound_translation_dispatch_failure(self):
        store_service = Mock()
        persistence_service = Mock()

        store_service.store_inbound_message.return_value = build_translation_record()
        persistence_service.create_persistence_event.return_value = build_persistence_event()

        service = BackgroundTasksService(store_service, persistence_service)
        # Dispatch returns False or fails
        service.dispatch_translation_event = Mock(return_value=False)

        result = service.persist_inbound_translation(
            ticket_id="TKT-100",
            customer_id=1,
            bilingual_message=build_bilingual_message()
        )
        
        assert result is False

    # ==========================================================
    # persist_outbound_translation
    # ==========================================================

    def test_persist_outbound_translation_success(self):
        store_service = Mock()
        persistence_service = Mock()
        persistence_service.persist_outbound_translation.return_value = True

        service = BackgroundTasksService(store_service, persistence_service)

        result = service.persist_outbound_translation(
            ticket_id="TKT-100",
            response_english="hello",
            response_translated="नमस्ते",
            response_language="hi"
        )

        assert result is True
        persistence_service.persist_outbound_translation.assert_called_once_with(
            ticket_id="TKT-100",
            response_english="hello",
            response_translated="नमस्ते",
            response_language="hi"
        )

    def test_persist_outbound_translation_failure(self):
        store_service = Mock()
        persistence_service = Mock()

        persistence_service.persist_outbound_translation.side_effect = Exception("update failure")

        service = BackgroundTasksService(store_service, persistence_service)

        # Should NOT raise, should return False
        result = service.persist_outbound_translation(
            ticket_id="TKT-100",
            response_english="hello",
            response_translated="नमस्ते",
            response_language="hi"
        )
        
        assert result is False

    # ==========================================================
    # dispatch_translation_event
    # ==========================================================

    def test_dispatch_translation_event_success(self):
        service = BackgroundTasksService(Mock(), Mock())
        event = build_persistence_event()

        result = service.dispatch_translation_event(event)
        assert result is True

    def test_dispatch_translation_event_serialization_failure(self):
        service = BackgroundTasksService(Mock(), Mock())

        bad_event = Mock()
        bad_event.event_id = "EVT-1"
        bad_event.model_dump_json.side_effect = Exception("serialization failed")

        # Should NOT raise
        result = service.dispatch_translation_event(bad_event)
        
        assert result is False