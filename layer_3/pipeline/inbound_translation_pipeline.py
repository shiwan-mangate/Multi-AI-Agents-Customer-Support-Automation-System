import logging
from typing import Optional

from layer_3.schemas.bilingual_message import BilingualMessage, LanguageContext
from layer_3.detection.detection_service import DetectionService
from layer_3.protection.format_and_entity_protector import FormatAndEntityProtector
from layer_3.translation.helsinki_translator import HelsinkiTranslator
from layer_3.translation.translation_validator import TranslationValidator
from layer_3.translation.translation_cache import TranslationCache

logger = logging.getLogger(__name__)

class InboundTranslationPipeline:
    """
    The Orchestrator for Layer 3 (Inbound).
    Converts raw customer messages in any language into safe, protected English 
    for the Supervisor Node, while generating deep language analytics.
    """

    def __init__(self):
        self.detection_service = DetectionService()
        self.protector = FormatAndEntityProtector()
        self.translator = HelsinkiTranslator()
        self.validator = TranslationValidator()
        self.cache = TranslationCache()

    def process_inbound(self, text: str, customer_context: Optional[dict] = None) -> BilingualMessage:
        """
        Executes the 10-step inbound translation workflow.
        """
       
        if not text or not text.strip():
            return self._build_fast_path_message(text, "en", 1.0, "empty_text")

       
        detection_result = self.detection_service.detect_language(text, customer_context)
        source_lang = detection_result.detected_language

       
        if source_lang == "en":
            logger.info("Inbound Pipeline | English Fast Path Triggered")
            return self._build_fast_path_message(text, source_lang, detection_result.confidence, detection_result.detection_method)

        logger.info(f"Inbound Pipeline | Translating from {source_lang} to en")

        
        protected_content = self.protector.protect(text)

        
        cached_result = self.cache.get(
            text=protected_content.protected_text,
            source_language=source_lang,
            target_language="en"
        )

        translation_failed = False
        fallback_triggered = False

        if cached_result:
          
            final_translated_text = cached_result.translated_text
            translation_success = cached_result.translation_success
        else:

            translation_result = self.translator.translate(
                text=protected_content.protected_text,
                source_language=source_lang,
                target_language="en"
            )

            
            is_valid = self.validator.validate(
                original_text=protected_content.protected_text,
                translated_text=translation_result.translated_text
            )

            if not is_valid or not translation_result.translation_success:
               
                logger.warning("Inbound Pipeline | Translation Validation Failed. Triggering Fallback.")
                final_translated_text = protected_content.protected_text  
                translation_failed = True
                fallback_triggered = True
            else:
                
                final_translated_text = translation_result.translated_text
                translation_success = True
                self.cache.set(
                    text=protected_content.protected_text,
                    source_language=source_lang,
                    target_language="en",
                    translation_result=translation_result
                )

        
        
        english_text = self.protector.restore(
            final_translated_text,
            protected_content
        )

      
        language_context = LanguageContext(
            detected_language=source_lang,
            detection_confidence=detection_result.confidence,
            detection_method=detection_result.detection_method,
            translation_used=True,
            translation_failed=translation_failed,
            fallback_triggered=fallback_triggered,
            mixed_language_detected=False, 
            script_detected=getattr(detection_result, 'script_detected', None)
        )

       
        logger.info("Inbound Pipeline | Processing Complete")
        return BilingualMessage(
            original_text=text,
            english_text=english_text,
            language_context=language_context
        )

    def _build_fast_path_message(self, text: str, lang: str, confidence: float, method: str) -> BilingualMessage:
        """Helper to construct a BilingualMessage when translation is skipped."""
        context = LanguageContext(
            detected_language=lang,
            detection_confidence=confidence,
            detection_method=method,
            translation_used=False,
            translation_failed=False,
            fallback_triggered=False,
            mixed_language_detected=False,
            script_detected=None
        )
        return BilingualMessage(
            original_text=text,
            english_text=text,
            language_context=context
        )