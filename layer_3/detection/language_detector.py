import logging
from typing import Tuple

# External Model Libraries
import fasttext
import langdetect
from langdetect.lang_detect_exception import LangDetectException

# Internal Architecture
from layer_3.detection.script_detector import ScriptDetector, Scripts
from layer_3.schemas.detection_result import DetectionResult
from layer_3.config.supported_languages import SCRIPT_LANGUAGE_MAP

logger = logging.getLogger(__name__)

class LanguageDetector:
    """
    Primary Language Classification Engine.
    Orchestrates Script Detection, FastText, and LangDetect to form a consensus.
    """

    def __init__(self, fasttext_model_path: str = "models/lid.176.ftz"):
        self.script_detector = ScriptDetector()
        
        # Fail Fast. A detection service without its primary model is a zombie.
        try:
            self.fasttext_model = fasttext.load_model(str(fasttext_model_path))
            logger.info(f"Successfully loaded fastText model from {fasttext_model_path}")
        except Exception as e:
            logger.error(f"CRITICAL: Failed to load fastText model from {fasttext_model_path}. Error: {e}")
            raise RuntimeError(f"LanguageDetector cannot start without fastText model: {e}")

    def detect(self, text: str) -> DetectionResult:
        """
        Main entry point for language detection.
        """
        if not text or not text.strip():
            return self._log_and_return(DetectionResult(
                detected_language="en",
                confidence=0.0,
                detection_method="empty_text",
                script_detected=Scripts.UNKNOWN
            ))

        # Step 1: Microsecond Script Detection
        script = self.script_detector.detect_script(text)

        # Step 2: Configuration-driven Fast-Path for deterministic scripts
        if script in SCRIPT_LANGUAGE_MAP:
            return self._log_and_return(DetectionResult(
                detected_language=SCRIPT_LANGUAGE_MAP[script],
                confidence=0.99,
                detection_method="script_fast_path",
                script_detected=script,
                mixed_language_detected=False,
                raw_detector_results={"script_detector": script}
            ))

        # Step 3: Latin / Mixed Script Path -> ML Models required
        ft_lang, ft_conf = self._detect_with_fasttext(text)
        ld_lang, ld_conf = self._detect_with_langdetect(text)

        raw_results = {
            "fasttext": {"lang": ft_lang, "confidence": ft_conf},
            "langdetect": {"lang": ld_lang, "confidence": ld_conf}
        }

        # Step 4: Consensus Logic
        result = self._build_consensus(script, ft_lang, ft_conf, ld_lang, ld_conf, raw_results)
        return self._log_and_return(result)

    def _build_consensus(self, script: str, ft_lang: str, ft_conf: float, ld_lang: str, ld_conf: float, raw_results: dict) -> DetectionResult:
        """
        Resolves conflicts between fastText and langdetect.
        """
        is_mixed_language = (ft_conf > 0.70 and ld_conf > 0.70 and ft_lang != ld_lang)

        # Case 1: Both models agree
        if ft_lang == ld_lang and ft_lang != "unknown":
            return DetectionResult(
                detected_language=ft_lang,
                confidence=max(ft_conf, ld_conf),
                detection_method="consensus",
                script_detected=script,
                mixed_language_detected=is_mixed_language,
                raw_detector_results=raw_results
            )

        # Case 2: Disagreement, but fastText is highly confident
        if ft_conf >= 0.80:
            return DetectionResult(
                detected_language=ft_lang,
                confidence=ft_conf,
                detection_method="fasttext_primary",
                script_detected=script,
                mixed_language_detected=is_mixed_language,
                raw_detector_results=raw_results
            )
        
        # Case 3: fastText failed/very weak, but langdetect is highly confident (The Rescue!)
        # FIX: Only let langdetect take over if fastText is highly uncertain (< 0.50)
        if ld_conf >= 0.80 and ld_lang != "unknown" and ft_conf < 0.50:
            return DetectionResult(
                detected_language=ld_lang,
                confidence=ld_conf,
                detection_method="langdetect_primary",
                script_detected=script,
                mixed_language_detected=is_mixed_language,
                raw_detector_results=raw_results
            )
        
        # Case 4: Both models weak and disagreeing
        # Find the best non-unknown fallback, defaulting to English
        fallback_lang = "en"
        if ft_lang != "unknown":
            fallback_lang = ft_lang
        elif ld_lang != "unknown":
            fallback_lang = ld_lang

        return DetectionResult(
            detected_language=fallback_lang,
            confidence=max(ft_conf, ld_conf), 
            detection_method="weak_signal",
            script_detected=script,
            mixed_language_detected=is_mixed_language,
            raw_detector_results=raw_results
        )

    def _detect_with_fasttext(self, text: str) -> Tuple[str, float]:
            """Wrapper for fastText prediction."""
            clean_text = text.replace('\n', ' ').strip()
            try:
                predictions = self.fasttext_model.predict(clean_text, k=1)
                lang_label = predictions[0][0].replace("__label__", "")
                confidence = float(predictions[1][0])
                return lang_label, confidence
            except Exception as e:
                logger.error(f"fastText prediction failed: {e}") # <--- Now we will see why it fails
                return "unknown", 0.0

    def _detect_with_langdetect(self, text: str) -> Tuple[str, float]:
        """Wrapper for langdetect prediction."""
        try:
            langs = langdetect.detect_langs(text)
            if langs:
                return langs[0].lang, langs[0].prob
            return "unknown", 0.0
        except LangDetectException:
            return "unknown", 0.0

    def _log_and_return(self, result: DetectionResult) -> DetectionResult:
        """Structured logging helper for full observability."""
        logger.info(
            f"Language Detection | "
            f"Script={result.script_detected} | "
            f"Language={result.detected_language} | "
            f"Method={result.detection_method} | "
            f"Confidence={result.confidence:.2f} | "
            f"Mixed={result.mixed_language_detected}"
        )
        return result