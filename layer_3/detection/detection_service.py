import logging
from typing import Optional
from layer_3.detection.language_detector import LanguageDetector
from layer_3.detection.context_signal_resolver import ContextSignalResolver
from layer_3.detection.script_detector import Scripts
from layer_3.schemas.detection_result import DetectionResult

logger = logging.getLogger(__name__)

class DetectionService:
    """
    The Facade for Layer 1: Language Detection Engine.
    Orchestrates the workflow between text-based ML detection and CRM-based contextual resolution.
    """
    def __init__(self, fasttext_model_path: str = "models/lid.176.ftz"):
     
        self.language_detector = LanguageDetector(fasttext_model_path)
        self.context_signal_resolver = ContextSignalResolver()

    def detect_language(self, text: str, customer_context: Optional[dict] = None) -> DetectionResult:
        """
        Coordinates the detection workflow. This is the sole public API boundary 
        for the entire detection layer.
        """
     
        logger.info(f"Language Detection Started | TextLength={len(text)}")

        try:
        
            initial_result = self.language_detector.detect(text)
          
            final_result = self.context_signal_resolver.resolve(
                text=text,
                detection_result=initial_result,
                customer_context=customer_context
            )

            logger.info(
                f"Language Detection Complete | "
                f"Language={final_result.detected_language} | "
                f"Method={final_result.detection_method} | "
                f"Confidence={final_result.confidence:.2f}"
            )
            return final_result

        except Exception as e:
            logger.error(f"CRITICAL: DetectionService encountered an unexpected error: {e}", exc_info=True)
            return DetectionResult(
                detected_language="en", 
                confidence=0.0,
                detection_method="service_fallback",
                script_detected=Scripts.UNKNOWN,
                mixed_language_detected=False,
              
                raw_detector_results={"error": str(e), "service": "DetectionService"}
            )