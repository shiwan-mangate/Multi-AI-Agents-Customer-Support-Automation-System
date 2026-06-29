import logging
import threading
from typing import Dict, Tuple
from transformers import MarianMTModel, MarianTokenizer

logger = logging.getLogger(__name__)

class ModelLoader:
    """
    Enterprise Model Manager.
    Ensures translation models are loaded exactly once per language pair.
    Prevents OOM errors and reduces 5000ms load times to 1ms cache hits.
    """
    
    _instance = None
    _lock = threading.Lock()

    SUPPORTED_MODELS = {
        # INBOUND: Customer Language -> English
        ("hi", "en"): "Helsinki-NLP/opus-mt-hi-en",
        ("es", "en"): "Helsinki-NLP/opus-mt-es-en",
        ("fr", "en"): "Helsinki-NLP/opus-mt-fr-en",
        ("de", "en"): "Helsinki-NLP/opus-mt-de-en",
        ("ar", "en"): "Helsinki-NLP/opus-mt-ar-en",
        
        # OUTBOUND: English -> Customer Language
        ("en", "hi"): "Helsinki-NLP/opus-mt-en-hi",
        ("en", "es"): "Helsinki-NLP/opus-mt-en-es",
        ("en", "fr"): "Helsinki-NLP/opus-mt-en-fr",
        ("en", "de"): "Helsinki-NLP/opus-mt-en-de",
        ("en", "ar"): "Helsinki-NLP/opus-mt-en-ar",
    }

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(ModelLoader, cls).__new__(cls)
                cls._instance._initialize()
            return cls._instance

    def _initialize(self):
        """Initializes the resource caches."""
        # Now stores tuples mapping to (tokenizer, model)
        self.loaded_models: Dict[Tuple[str, str], Tuple[MarianTokenizer, MarianMTModel]] = {}
        logger.info("ModelLoader Initialized.")

    def is_loaded(self, source_language: str, target_language: str = "en") -> bool:
        """Checks if a specific language pair model is currently loaded in memory."""
        pair_key = (source_language, target_language)
        return pair_key in self.loaded_models

    def get_loaded_models(self) -> list[str]:
        """Returns a list of all currently loaded language pairs."""
        return [f"{src}-{tgt}" for src, tgt in self.loaded_models.keys()]

    def get_model(self, source_language: str, target_language: str = "en") -> tuple:
        """
        Returns the tokenizer and model for the requested language pair.
        Loads them into memory if not already present.
        """
        pair_key = (source_language, target_language)

        if pair_key not in self.SUPPORTED_MODELS:
            raise ValueError(f"Language pair '{source_language}-{target_language}' is not supported by the platform.")

        # Fast path: already loaded
        if self.is_loaded(source_language, target_language):
            return self.loaded_models[pair_key]

        # Thread-safe loading path
        with self._lock:
            # Double-check inside the lock to prevent race conditions
            if self.is_loaded(source_language, target_language):
                return self.loaded_models[pair_key]

            model_name = self.SUPPORTED_MODELS[pair_key]
            logger.info(f"ModelLoader | Loading {model_name} into memory. This will take a moment...")

            try:
                tokenizer = MarianTokenizer.from_pretrained(model_name)
                model = MarianMTModel.from_pretrained(model_name)
                
                self.loaded_models[pair_key] = (tokenizer, model)
                
                logger.info(f"ModelLoader | Successfully cached {model_name}.")
                return tokenizer, model

            except Exception as e:
                logger.error(f"CRITICAL: Failed to load model {model_name} | Error={e}", exc_info=True)
                raise RuntimeError(f"Could not load translation resources for {source_language}-{target_language}") from e