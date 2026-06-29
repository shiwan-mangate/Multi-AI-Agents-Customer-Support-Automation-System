import sys
import os

# Dynamically add layer_3 to the Python path
layer_3_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if layer_3_path not in sys.path:
    sys.path.insert(0, layer_3_path)

import pytest
from unittest.mock import patch, MagicMock

from layer_3.pipeline.inbound_translation_pipeline import InboundTranslationPipeline
from layer_3.schemas.bilingual_message import BilingualMessage
from layer_3.schemas.translation_result import TranslationResult

class TestInboundTranslationPipeline:

    @pytest.fixture
    @patch("pipeline.inbound_translation_pipeline.DetectionService")
    @patch("pipeline.inbound_translation_pipeline.HelsinkiTranslator")
    def pipeline(self, MockTranslator, MockDetectionService):
        pipe = InboundTranslationPipeline()
        pipe.cache.clear()
        return pipe

    # Test 1 — Empty String
    def test_empty_string(self, pipeline):
        result = pipeline.process_inbound("   ")
        assert isinstance(result, BilingualMessage)
        assert result.english_text == "   "
        assert result.language_context.detected_language == "en"
        assert result.language_context.translation_used is False

    # Test 2 — English Fast Path
    def test_english_fast_path(self, pipeline):
        pipeline.detection_service.detect_language.return_value = MagicMock(
            detected_language="en", confidence=0.99, detection_method="fast_text", script_detected=None
        )
        
        text = "Where is my order ORD-123?"
        result = pipeline.process_inbound(text)
        
        assert result.english_text == text
        assert result.language_context.translation_used is False
        assert pipeline.cache.size() == 0
        pipeline.translator.translate.assert_not_called()

    # Test 3 — Full Translation Flow (Cache Miss)
    def test_full_translation_flow(self, pipeline):
        pipeline.detection_service.detect_language.return_value = MagicMock(
            detected_language="hi", confidence=0.98, detection_method="fast_text", script_detected=None
        )
        
        def mock_translate_side_effect(text, source_language, target_language):
            assert "__ORDER_ID_1__" in text
            return TranslationResult(
                translated_text="Hello where is my order __ORDER_ID_1__",
                source_language="hi",
                target_language="en",
                translation_service="helsinki",
                translation_success=True
            )
        pipeline.translator.translate.side_effect = mock_translate_side_effect

        input_text = "नमस्ते मेरा order ORD-123 कहाँ है?"
        result = pipeline.process_inbound(input_text)

        assert result.original_text == input_text
        assert result.english_text == "Hello where is my order ORD-123" 
        assert result.language_context.translation_used is True
        assert result.language_context.translation_failed is False
        assert pipeline.cache.size() == 1 

    # Test 4 — Cache Hit (Skips Translation)
    def test_cache_hit_flow(self, pipeline):
        pipeline.detection_service.detect_language.return_value = MagicMock(
            detected_language="es", confidence=0.99, detection_method="fast_text", script_detected=None
        )
        
        pipeline.cache.set(
            text="Hola __ORDER_ID_1__",
            source_language="es",
            target_language="en",
            translation_result=TranslationResult(
                translated_text="Hello __ORDER_ID_1__",
                source_language="es",
                target_language="en",
                translation_service="helsinki",
                translation_success=True
            )
        )

        result = pipeline.process_inbound("Hola ORD-999")

        pipeline.translator.translate.assert_not_called()
        assert result.english_text == "Hello ORD-999"

    
    def test_validation_failure_fallback(self, pipeline):
        pipeline.detection_service.detect_language.return_value = MagicMock(
            detected_language="fr", confidence=0.99, detection_method="fast_text", script_detected=None
        )
        
        pipeline.translator.translate.return_value = TranslationResult(
            translated_text="Hello where is my order", 
            source_language="fr",
            target_language="en",
            translation_service="helsinki",
            translation_success=True
        )

        input_text = "Bonjour commande ORD-555"
        result = pipeline.process_inbound(input_text)

        assert result.english_text == input_text
        assert result.language_context.translation_failed is True
        assert result.language_context.fallback_triggered is True
        assert pipeline.cache.size() == 0