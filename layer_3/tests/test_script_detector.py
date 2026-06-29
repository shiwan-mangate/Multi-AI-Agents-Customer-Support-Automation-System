import pytest
from layer_3.detection.script_detector import ScriptDetector, Scripts
class TestScriptDetector:
    
    @pytest.fixture
    def detector(self):
        """Provides a fresh instance of the detector for each test."""
        return ScriptDetector()

    @pytest.mark.parametrize("text, expected_script", [
        # Standard Latin
        ("Hello world", Scripts.LATIN),
        
        # Target Scripts
        ("मेरा ऑर्डर कहाँ है", Scripts.DEVANAGARI),
        ("مرحبا", Scripts.ARABIC),
        ("Привет", Scripts.CYRILLIC),
        ("안녕하세요", Scripts.HANGUL),
        ("你好", Scripts.CJK),
        
        # Edge Cases & Empty Inputs
        ("", Scripts.UNKNOWN),
        ("   ", Scripts.UNKNOWN),
        ("12345!!!", Scripts.UNKNOWN),
        
        # Mixed/Transliterated
        ("Mera order kaha hai", Scripts.LATIN),
        ("Refund मेरा", Scripts.DEVANAGARI), # Should catch Devanagari over Latin
    ])
    def test_detect_script(self, detector: ScriptDetector, text: str, expected_script: str):
        """Ensures the script detector correctly maps strings to their primary script."""
        assert detector.detect_script(text) == expected_script