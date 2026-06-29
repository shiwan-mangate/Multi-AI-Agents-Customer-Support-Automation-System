import re
import logging

logger = logging.getLogger(__name__)

class TranslationValidator:
    """
    Quality Assurance for the Translation Layer.
    Ensures that the LLM/Neural Network did not hallucinate, corrupt, 
    drop critical placeholders, or produce length anomalies.
    """

    def __init__(self):
        self.placeholder_pattern = re.compile(r"__[A-Z_]+_\d+__")

    def validate(self, original_text: str, translated_text: str) -> bool:
        """
        Executes a sequence of validation rules to guarantee translation integrity.
        Returns True if safe, False if the translation should be rejected.
        """

        if not original_text or not original_text.strip():
            is_valid_empty = not translated_text or not translated_text.strip()
            if not is_valid_empty:
                logger.error("Translation Validation Failed | Reason=EmptyInputHallucination")
            return is_valid_empty

        if not self._validate_empty_output(original_text, translated_text):
            logger.error("Translation Validation Failed | Reason=EmptyOutput")
            return False

        if not self._validate_placeholders(original_text, translated_text):
            logger.error("Translation Validation Failed | Reason=PlaceholderLostOrCorrupted")
            return False

        if not self._validate_length_drift(original_text, translated_text):
            logger.error("Translation Validation Failed | Reason=ExcessiveLengthDrift")
            return False

        if not self._validate_minimum_content(original_text, translated_text):
            logger.error("Translation Validation Failed | Reason=SuspiciouslyTinyOutput")
            return False

        logger.info("Translation Validation Passed")
        return True

    def _validate_empty_output(self, original_text: str, translated_text: str) -> bool:
        """Rejects translations where the model output absolutely nothing."""
        if not translated_text or not translated_text.strip():
            return False
        return True

    def _validate_placeholders(self, original_text: str, translated_text: str) -> bool:
        """
        Extracts all placeholders from the original text and ensures 
        every single one survived in the translated text exactly as formatted.
        """
        original_placeholders = set(self.placeholder_pattern.findall(original_text))
        
        for placeholder in original_placeholders:
            if placeholder not in translated_text:
                return False
        return True

    def _validate_length_drift(self, original_text: str, translated_text: str) -> bool:
        """
        Rejects severe hallucinations where the model loops or generates essays.
        e.g., A 10-character input should not result in a 500-character output.
        """
        original_len = len(original_text)
        translated_len = len(translated_text)

        if original_len < 20 and translated_len > 100:
            return False
            
    
        if original_len >= 20 and translated_len > (original_len * 3.5):
            return False
            
        return True

    def _validate_minimum_content(self, original_text: str, translated_text: str) -> bool:
        """
        Rejects suspiciously truncated outputs.
        e.g., A 200-character input returning just "ok".
        """
        original_len = len(original_text)
        translated_len = len(translated_text)
        

        if original_len < 20:
            return True
            
        if translated_len < (original_len * 0.15):
            return False
            
        return True