import logging
from layer_3.translation.model_loader import ModelLoader
from layer_3.schemas.translation_result import TranslationResult

logger = logging.getLogger(__name__)

class HelsinkiTranslator:
    """
    Core Translation Engine for Layer 3.
    Orchestrates tokenization, model inference, and decoding using Helsinki-NLP.
    Never raises exceptions to the caller; returns safe TranslationResult objects.
    """

    def __init__(self):
        self.model_loader = ModelLoader()
        # Set Provider Name dynamically so future providers (DeepL, AWS) can easily slot in
        self.provider_name = "helsinki"

    def translate(self, text: str, source_language: str, target_language: str = "en") -> TranslationResult:
        """
        Translates text deterministically. Expects format-protected text.
        """
        
        # Guard 1: Empty text
        if not text or not text.strip():
            return TranslationResult(
                translated_text=text if text is not None else "",
                source_language=source_language,
                target_language=target_language,
                translation_service=self.provider_name,
                translation_success=True,
                translation_confidence=None
            )

        # Guard 2: Source and Target are the same (Fast Path bypass)
        if source_language == target_language:
            logger.info(f"Translation Skipped | Source == Target ({source_language})")
            return TranslationResult(
                translated_text=text,
                source_language=source_language,
                target_language=target_language,
                translation_service=self.provider_name,
                translation_success=True,
                translation_confidence=None
            )

        logger.info(f"Translation Started | Source={source_language} | Target={target_language} | InputLength={len(text)}")

        try:
            # 1. Fetch the correct bi-directional model/tokenizer
            tokenizer, model = self.model_loader.get_model(source_language, target_language)

            # 2. Tokenize Input
            inputs = tokenizer(
                text, 
                return_tensors="pt", 
                padding=True, 
                truncation=True, 
                max_length=512
            )

            # 3. Generate Translation
            translated_tokens = model.generate(
                **inputs,
                max_length=512,
                num_beams=4,
                early_stopping=True
            )

            # 4. Decode Output
            translated_text = tokenizer.decode(
                translated_tokens[0], 
                skip_special_tokens=True
            )

            logger.info(
                f"Translation Complete | "
                f"Source={source_language} | "
                f"Target={target_language} | "
                f"InputLength={len(text)} | "
                f"OutputLength={len(translated_text)}"
            )

            return TranslationResult(
                translated_text=translated_text,
                source_language=source_language,
                target_language=target_language,
                translation_service=self.provider_name,
                translation_success=True,
                translation_confidence=None
            )

        except Exception as e:
            logger.error(
                f"Translation Failed | Source={source_language} | Target={target_language} | "
                f"InputLength={len(text)} | Error={e}", 
                exc_info=True
            )
            
            # Safe Fallback to the original untranslated text
            return TranslationResult(
                translated_text=text,
                source_language=source_language,
                target_language=target_language,
                translation_service=self.provider_name,
                translation_success=False,
                translation_confidence=None
            )