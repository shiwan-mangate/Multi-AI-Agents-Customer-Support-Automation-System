import pytest
from layer_3.detection.context_signal_resolver import ContextSignalResolver
from layer_3.schemas.detection_result import DetectionResult

class TestContextSignalResolver:

    @pytest.fixture
    def resolver(self):
        """Provides a fresh instance of the resolver."""
        return ContextSignalResolver()

    def _make_result(self, lang: str, conf: float, method: str = "weak_signal") -> DetectionResult:
        """Helper to quickly generate DetectionResult objects for testing."""
        return DetectionResult(
            detected_language=lang,
            confidence=conf,
            detection_method=method,
            script_detected="latin",
            mixed_language_detected=False,
            raw_detector_results={}
        )

    def test_high_confidence_remains_unchanged(self, resolver: ContextSignalResolver):
        """Rule 1: If the models are highly confident, do not override, even if CRM says otherwise."""
        original = self._make_result("en", 0.95, "consensus")
        context = {"preferred_language": "hi"}
        
        resolved = resolver.resolve("Hello", original, context)
        
        assert resolved.detected_language == "en"
        assert resolved.confidence == 0.95
        assert resolved.detection_method == "consensus"

    def test_strong_french_detection_not_overridden(self, resolver: ContextSignalResolver):
        """Rule 5: Strong detection always wins (User switching languages)."""
        original = self._make_result("fr", 0.88, "fasttext_primary")
        context = {"preferred_language": "es", "history": ["es", "es"]}
        
        resolved = resolver.resolve("Bonjour", original, context)
        
        assert resolved.detected_language == "fr"

    def test_no_context_remains_unchanged(self, resolver: ContextSignalResolver):
        """If CRM context is missing or empty, return the original weak signal."""
        original = self._make_result("en", 0.40)
        
        # Test None
        assert resolver.resolve("test", original, None) == original
        # Test Empty Dict
        assert resolver.resolve("test", original, {}) == original

    def test_preferred_language_override(self, resolver: ContextSignalResolver):
        """Rule 2: Preferred language rescues a weak signal."""
        original = self._make_result("en", 0.40)
        context = {"preferred_language": "hi"}
        
        resolved = resolver.resolve("Mera refund", original, context)
        
        assert resolved.detected_language == "hi"
        assert resolved.confidence == 0.85
        assert resolved.detection_method == "preferred_language_override"

    def test_history_override_with_dominance(self, resolver: ContextSignalResolver):
        """Rule 3: History overrides if the dominant language > 60%."""
        original = self._make_result("en", 0.40)
        # 'es' is 4/5 = 80% dominant
        context = {"language_history": ["es", "es", "es", "en", "es"]}
        
        resolved = resolver.resolve("Hola", original, context)
        
        assert resolved.detected_language == "es"
        assert resolved.confidence == 0.80
        assert resolved.detection_method == "history_override"

    def test_history_rejected_due_to_low_dominance(self, resolver: ContextSignalResolver):
        """Rule 3 Extension: Noisy history (< 60% dominance) should NOT override."""
        original = self._make_result("en", 0.45)
        # 'hi' is 2/5 = 40% dominant
        context = {"language_history": ["hi", "en", "hi", "en", "es"]}
        
        resolved = resolver.resolve("Help", original, context)
        
        # Should remain 'en' because history is too noisy to trust
        assert resolved.detected_language == "en"
        assert resolved.detection_method == "weak_signal"

    def test_empty_history(self, resolver: ContextSignalResolver):
        """Ensures an empty history list is handled safely without division by zero."""
        original = self._make_result("en", 0.40)
        context = {"language_history": []}
        
        resolved = resolver.resolve("test", original, context)
        assert resolved.detected_language == "en"

    def test_locale_assist(self, resolver: ContextSignalResolver):
        """Rule 4: Browser locale rescues signal if no better context exists."""
        original = self._make_result("en", 0.35)
        context = {"browser_locale": "de-DE"}
        
        resolved = resolver.resolve("test", original, context)
        
        assert resolved.detected_language == "de"
        assert resolved.confidence == 0.70
        assert resolved.detection_method == "locale_override"

    def test_unsupported_language_ignored(self, resolver: ContextSignalResolver):
        """Validation: A rogue CRM value (unsupported language) is safely ignored."""
        original = self._make_result("en", 0.40)
        # 'xyz' is not in SUPPORTED_LANGUAGES, 'it' (Italian) is not supported in MVP
        context = {
            "preferred_language": "xyz",
            "browser_locale": "it-IT"
        }
        
        resolved = resolver.resolve("test", original, context)
        
        assert resolved.detected_language == "en"
        assert resolved.detection_method == "weak_signal"

    def test_conflicting_signals_priority(self, resolver: ContextSignalResolver):
        """Priority check: Preference > History > Locale."""
        original = self._make_result("en", 0.40)
        
        context = {
            "preferred_language": "hi",                      # Priority 1
            "language_history": ["es", "es", "es", "es"],    # Priority 2
            "browser_locale": "fr-FR"                        # Priority 3
        }
        
        resolved = resolver.resolve("test", original, context)
        
        # 'hi' must win because preferred_language is evaluated first
        assert resolved.detected_language == "hi"
        assert resolved.detection_method == "preferred_language_override"