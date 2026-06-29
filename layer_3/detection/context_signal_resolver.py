import logging
from typing import Optional, List
from collections import Counter

from layer_3.schemas.detection_result import DetectionResult

logger = logging.getLogger(__name__)

class ContextSignalResolver:
    """
    Layer 3: Customer Intelligence.
    Rescues weak language detection signals using decoupled CRM context.
    """

    # Rule 1 & Rule 5: Strong detection always wins.
    STRONG_SIGNAL_THRESHOLD = 0.80
    
    # Validation constraint: Only allow overrides into languages the platform actually supports.
    SUPPORTED_LANGUAGES = {"en", "hi", "es", "fr", "de", "ar", "ko", "zh", "pt"}

    def resolve(
        self, 
        text: str, 
        detection_result: DetectionResult, 
        customer_context: Optional[dict] = None
    ) -> DetectionResult:
        """
        Evaluates a DetectionResult against customer context and upgrades 
        confidence/language if the original signal is weak.
        """
        if not customer_context:
            return detection_result

        if not self._should_apply_override(detection_result):
            return detection_result

        original_lang = detection_result.detected_language
        logger.info(
            f"Evaluating weak signal (Lang: {original_lang}, "
            f"Conf: {detection_result.confidence:.2f}) against customer context."
        )

        # Evaluate the cascade in priority order
        resolved_result = (
            self._apply_preferred_language(detection_result, customer_context) or
            self._apply_history_signal(detection_result, customer_context) or
            self._apply_locale_signal(detection_result, customer_context)
        )

        # If any of the contextual rules triggered an override, log the transformation
        if resolved_result:
            logger.info(
                f"Language Override | "
                f"Method={resolved_result.detection_method} | "
                f"Original={original_lang} | "
                f"Resolved={resolved_result.detected_language}"
            )
            return resolved_result

        return detection_result

    def _should_apply_override(self, result: DetectionResult) -> bool:
        """Determines if the signal is weak enough to require contextual rescue."""
        return (
            result.confidence < self.STRONG_SIGNAL_THRESHOLD or 
            result.detection_method == "weak_signal"
        )

    def _apply_preferred_language(self, result: DetectionResult, context: dict) -> Optional[DetectionResult]:
        """Applies the strongest contextual signal: validated user-defined preference."""
        pref_lang = context.get("preferred_language")
        
        # Validation: Ensure the CRM data is actually a language we support
        if pref_lang and pref_lang in self.SUPPORTED_LANGUAGES:
            return DetectionResult(
                detected_language=pref_lang,
                confidence=0.85, 
                detection_method="preferred_language_override",
                script_detected=result.script_detected,
                mixed_language_detected=result.mixed_language_detected,
                raw_detector_results=result.raw_detector_results
            )
        return None

    def _apply_history_signal(self, result: DetectionResult, context: dict) -> Optional[DetectionResult]:
        """Looks for a dominant language in the customer's recent ticket history."""
        history: List[str] = context.get("language_history", [])
        if not history:
            return None

        # Extract frequency
        counter = Counter(history)
        lang, count = counter.most_common(1)[0]
        
        # Dominance Check: The language must represent a clear majority of their history
        dominance = count / len(history)
        if dominance < 0.60:
            return None
            
        # Validation: Ensure the dominant language is supported
        if lang not in self.SUPPORTED_LANGUAGES:
            return None

        return DetectionResult(
            detected_language=lang,
            confidence=0.80,
            detection_method="history_override",
            script_detected=result.script_detected,
            mixed_language_detected=result.mixed_language_detected,
            raw_detector_results=result.raw_detector_results
        )

    def _apply_locale_signal(self, result: DetectionResult, context: dict) -> Optional[DetectionResult]:
        """Uses the browser locale as a supporting signal."""
        locale: str = context.get("browser_locale")
        if not locale:
            return None

        base_lang = locale.split("-")[0].lower()
        
        if base_lang in self.SUPPORTED_LANGUAGES:
            return DetectionResult(
                detected_language=base_lang,
                confidence=0.70, 
                detection_method="locale_override",
                script_detected=result.script_detected,
                mixed_language_detected=result.mixed_language_detected,
                raw_detector_results=result.raw_detector_results
            )
        return None