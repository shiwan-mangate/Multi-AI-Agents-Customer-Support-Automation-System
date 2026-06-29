import sys
import os

# Dynamically add layer_3 to the Python path
layer_3_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if layer_3_path not in sys.path:
    sys.path.insert(0, layer_3_path)

import pytest
from unittest.mock import patch, MagicMock

from layer_3.pipeline.outbound_translation_pipeline import OutboundTranslationPipeline
from layer_3.schemas.translation_result import TranslationResult

class TestOutboundTranslationPipeline:

    @pytest.fixture
    @patch("pipeline.outbound_translation_pipeline.HelsinkiTranslator")
    def pipeline(self, MockTranslator):
        """Yields a fresh pipeline with a clean cache and mocked ML models."""
        pipe = OutboundTranslationPipeline()
        pipe.cache.clear()
        return pipe


    def test_empty_input(self, pipeline):
        result = pipeline.process_outbound("", "hi")
        assert result.translated_text == ""
        assert result.translation_success is True
        assert result.target_language == "hi"

    def test_english_fast_path(self, pipeline):
        english_response = "Your refund has been approved."
        result = pipeline.process_outbound(english_response, "en")
        
        assert result.translated_text == english_response
        assert result.translation_success is True
        assert result.target_language == "en"
        pipeline.translator.translate.assert_not_called()

    def test_unsupported_language(self, pipeline):
        english_response = "Your refund has been approved."
        result = pipeline.process_outbound(english_response, "ru") # 'ru' is not in SUPPORTED_OUTBOUND_LANGUAGES
        
        assert result.translated_text == english_response
        assert result.translation_success is False
        assert result.target_language == "ru"
        pipeline.translator.translate.assert_not_called()


    def test_translation_success(self, pipeline):
        pipeline.translator.translate.return_value = TranslationResult(
            translated_text="आपका रिफंड स्वीकृत कर दिया गया है।",
            source_language="en",
            target_language="hi",
            translation_service="helsinki",
            translation_success=True
        )

        english_response = "Your refund has been approved."
        result = pipeline.process_outbound(english_response, "hi")

        assert result.translation_success is True
        assert result.target_language == "hi"
        assert result.translated_text != english_response

    def test_order_id_preservation(self, pipeline):
        def mock_translate(text, source_language, target_language):
            assert "__ORDER_ID_1__" in text
            return TranslationResult(
                translated_text="आपका रिफंड __ORDER_ID_1__ स्वीकृत कर दिया गया है।",
                source_language="en", target_language="hi", translation_service="helsinki", translation_success=True
            )
        pipeline.translator.translate.side_effect = mock_translate

        result = pipeline.process_outbound("Your refund for ORD-12345 has been approved.", "hi")
        assert "ORD-12345" in result.translated_text
        assert "__ORDER_ID_1__" not in result.translated_text

    def test_email_preservation(self, pipeline):
        def mock_translate(text, source_language, target_language):
            assert "__EMAIL_1__" in text
            return TranslationResult(
                translated_text="संपर्क करें __EMAIL_1__",
                source_language="en", target_language="hi", translation_service="helsinki", translation_success=True
            )
        pipeline.translator.translate.side_effect = mock_translate

        result = pipeline.process_outbound("Contact john@example.com", "hi")
        assert "john@example.com" in result.translated_text


    def test_cache_miss(self, pipeline):
        pipeline.translator.translate.return_value = TranslationResult(
            translated_text="रिफंड", source_language="en", target_language="hi", translation_service="helsinki", translation_success=True
        )
        
        assert pipeline.cache.size() == 0
        pipeline.process_outbound("Refund", "hi")
        
        pipeline.translator.translate.assert_called_once()
        assert pipeline.cache.size() == 1

    def test_cache_hit(self, pipeline):
       
        pipeline.cache.set(
            text="Refund",
            source_language="en",
            target_language="hi",
            translation_result=TranslationResult(
                translated_text="रिफंड", source_language="en", target_language="hi", translation_service="helsinki", translation_success=True
            )
        )

        result = pipeline.process_outbound("Refund", "hi")
        pipeline.translator.translate.assert_not_called()
        assert result.translated_text == "रिफंड"


    def test_translation_failure(self, pipeline):
        english_response = "Refund approved."
        pipeline.translator.translate.return_value = TranslationResult(
            translated_text=english_response, source_language="en", target_language="hi", translation_service="helsinki", translation_success=False
        )

        result = pipeline.process_outbound(english_response, "hi")
        
        assert result.translation_success is False
        assert result.translated_text == english_response

    def test_validation_failure(self, pipeline):
        english_response = "Refund for ORD-123 approved."
       
        pipeline.translator.translate.return_value = TranslationResult(
            translated_text="रिफंड स्वीकृत।", 
            source_language="en", target_language="hi", translation_service="helsinki", translation_success=True
        )

        result = pipeline.process_outbound(english_response, "hi")
        
        
        assert result.translation_success is False
        assert result.translated_text == english_response


    def test_restore_entities(self, pipeline):
        english_response = "Refund approved for ORD-55555."
        
        pipeline.translator.translate.return_value = TranslationResult(
            translated_text="रिफंड __ORDER_ID_1__ के लिए स्वीकृत।",
            source_language="en", target_language="hi", translation_service="helsinki", translation_success=True
        )

        result = pipeline.process_outbound(english_response, "hi")
        
        
        assert "__ORDER_ID_" not in result.translated_text
        assert "ORD-55555" in result.translated_text

    def test_end_to_end_refund_response(self, pipeline):
        english_response = """
        Your refund for ORD-12345
        has been approved.

        Transaction ID: TXN-555

        Contact support@example.com
        if you need help.
        """

        def mock_translate_e2e(text, source_language, target_language):
            # Assert that the Protector abstracted the known complex entities perfectly
            assert "__ORDER_ID_1__" in text
            assert "__EMAIL_1__" in text
            
            return TranslationResult(
                translated_text="""
                __ORDER_ID_1__ का रिफंड स्वीकृत।
                ट्रांजैक्शन: TXN-555
                संपर्क करें: __EMAIL_1__
                """,
                source_language="en", target_language="hi", translation_service="helsinki", translation_success=True
            )
            
        pipeline.translator.translate.side_effect = mock_translate_e2e

        result = pipeline.process_outbound(english_response, "hi")

        # Verify all entities survived the round trip back into the foreign string
        assert "ORD-12345" in result.translated_text
        assert "TXN-555" in result.translated_text
        assert "support@example.com" in result.translated_text
        assert result.translation_success is True