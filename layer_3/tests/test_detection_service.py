import pytest
from unittest.mock import patch

from layer_3.detection.detection_service import DetectionService

class TestDetectionService:

    @pytest.fixture(scope="class")
    def service(self):
        """
        Loads the DetectionService and the heavy fastText model 
        ONCE for all tests in this class to ensure fast test execution.
        """
        return DetectionService(fasttext_model_path="models/lid.176.ftz")

    def test_normal_english_flow(self, service: DetectionService):
        """Validates that a standard English message flows through without interference."""
        result = service.detect_language("My refund has not arrived", customer_context=None)
        
        assert result.detected_language == "en"
        assert result.confidence > 0.80
        # Will be 'consensus' if langdetect agrees, or 'fasttext_primary'
        assert result.detection_method in ["consensus", "fasttext_primary"]

    def test_weak_signal_with_override_flow(self, service: DetectionService):
        """Validates the resolver is correctly invoked to override weak signals."""
        # Pure symbols guarantee a weak signal from the NLP models
        text = "@@@###123!!!" 
        context = {"preferred_language": "hi"}
        
        result = service.detect_language(text, customer_context=context)
        
        # Models guess 'en'/'unknown' (weak_signal), but resolver upgrades to Hindi
        assert result.detected_language == "hi"
        assert result.confidence == 0.85
        assert result.detection_method == "preferred_language_override"

    def test_no_context_flow(self, service: DetectionService):
        """Validates behavior when no CRM context is provided (returns original ML result)."""
        text = "Hola, mi pedido no ha llegado"
        result = service.detect_language(text, customer_context=None)
        
        assert result.detected_language == "es"
        assert result.confidence > 0.80

    def test_empty_text_flow(self, service: DetectionService):
        """Validates empty strings trigger the fast-fail empty_text logic."""
        result = service.detect_language("   ", customer_context=None)
        
        assert result.detected_language == "en"
        assert result.confidence == 0.0
        assert result.detection_method == "empty_text"

    @patch("detection.language_detector.LanguageDetector.detect")
    def test_service_fallback_on_exception(self, mock_detect, service: DetectionService):
        """
        Validates that unexpected crashes degrade gracefully rather than 
        breaking the entire translation pipeline.
        """
        # Force the underlying language detector to throw a fatal error
        mock_detect.side_effect = RuntimeError("Simulated fastText memory corruption")
        
        result = service.detect_language("Test message", customer_context=None)
        
        # The service should catch the error and return a safe fallback DetectionResult
        assert result.detected_language == "en"
        assert result.confidence == 0.0
        assert result.detection_method == "service_fallback"
        assert result.script_detected == "unknown"
        
        # Verify the error string is captured for observability
        assert "Simulated fastText memory corruption" in result.raw_detector_results.get("error", "")
        assert result.raw_detector_results.get("service") == "DetectionService"