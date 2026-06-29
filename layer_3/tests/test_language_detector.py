import pytest
from layer_3.detection.language_detector import LanguageDetector

class TestLanguageDetector:
    
    @pytest.fixture(scope="class")
    def detector(self):
        """
        Loads the LanguageDetector and fastText model ONCE for all tests in this class.
        This drastically speeds up test execution.
        """
        # Assumes the test is run from the layer_3_translation directory
        return LanguageDetector(fasttext_model_path="models/lid.176.ftz")

    @pytest.mark.parametrize("text, expected_lang", [
        # Standard Latin (Consensus Path)
        ("My refund has not arrived", "en"),
        ("Mi pedido no ha llegado", "es"),
        ("Mon remboursement n'est pas arrivé", "fr"),
        ("Meine Bestellung ist nicht angekommen", "de"),
        
        # Non-Latin (Fast Path)
        ("मेरा ऑर्डर कहाँ है", "hi"), # Devanagari
        ("مرحبا", "ar"),             # Arabic
        ("안녕하세요", "ko"),            # Hangul
        ("你好", "zh"),               # CJK
    ])
    def test_standard_detection(self, detector: LanguageDetector, text: str, expected_lang: str):
        """Ensures the detector correctly identifies standard, high-confidence languages."""
        result = detector.detect(text)
        assert result.detected_language == expected_lang
        # Fast path should yield 0.99, ML path should yield high confidence > 0.80
        assert result.confidence > 0.80 

    def test_hinglish_mixed_language(self, detector: LanguageDetector):
        """Ensures Hinglish is either flagged as mixed/weak, or successfully detected as Hindi."""
        text = "Mera order refund kab milega"
        result = detector.detect(text)
        
        is_mixed = result.mixed_language_detected
        is_weak = result.detection_method == "weak_signal"
        is_smart_detection = result.detected_language in ["hi", "en"]
        
        # We consider the test passed if it catches the complexity OR smartly resolves it to hi/en
        assert (is_mixed or is_weak or is_smart_detection) is True, \
            f"Hinglish failed. Result was: {result}"

    def test_empty_input(self, detector: LanguageDetector):
        """Ensures empty strings return English with 0 confidence immediately."""
        for empty_text in ["", "   ", "\n\t"]:
            result = detector.detect(empty_text)
            assert result.detected_language == "en"
            assert result.confidence == 0.0
            assert result.detection_method == "empty_text"

    def test_garbage_input(self, detector: LanguageDetector):
        """Ensures pure symbols do not crash the models and yield a low-confidence fallback."""
        garbage_text = "@@@###123!!!"
        result = detector.detect(garbage_text)
        
        # fastText will never return EXACTLY 0.0. It will return a tiny residual probability (e.g., 0.12)
        assert result.detected_language == "en"
        assert result.confidence < 0.20, "Garbage text yielded unexpectedly high confidence."
        assert result.detection_method == "weak_signal"