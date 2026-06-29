import hashlib
import logging
import threading
from typing import Optional
from layer_3.schemas.translation_result import TranslationResult

logger = logging.getLogger(__name__)

class TranslationCache:
    """
    Thread-Safe Singleton Translation Cache.
    Prevents redundant LLM/Neural Network inference by storing and retrieving 
    previously translated strings using a deterministic SHA-256 hash key.
    """
    
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(TranslationCache, cls).__new__(cls)
                cls._instance._initialize()
            return cls._instance

    def _initialize(self):
        """Initializes the in-memory cache."""
        self._cache: dict[str, TranslationResult] = {}
        logger.info("TranslationCache Initialized.")

    def _generate_key(self, text: str, source_language: str, target_language: str) -> str:
        """
        Generates a deterministic SHA-256 hash to prevent memory bloat 
        from storing large strings as dictionary keys.
        """
        raw_key = f"{source_language}::{target_language}::{text}"
        return hashlib.sha256(raw_key.encode('utf-8')).hexdigest()

    def get(self, text: str, source_language: str, target_language: str = "en") -> Optional[TranslationResult]:
        """
        Retrieves a TranslationResult from the cache if it exists.
        Returns None on a Cache Miss.
        """
        if not text or not text.strip():
            return None

        key = self._generate_key(text, source_language, target_language)

        with self._lock:
            result = self._cache.get(key)
            
        if result:
            logger.info(f"Translation Cache Hit | Source={source_language} | Target={target_language}")
            return result
            
        logger.info(f"Translation Cache Miss | Source={source_language} | Target={target_language}")
        return None

    def set(self, text: str, source_language: str, target_language: str, translation_result: TranslationResult) -> None:
        """
        Stores a TranslationResult in the cache.
        """
        if not text or not text.strip() or not translation_result:
            return

        key = self._generate_key(text, source_language, target_language)

        with self._lock:
            self._cache[key] = translation_result
            logger.info(f"Translation Cache Store | Source={source_language} | Target={target_language}")
            
    def clear(self) -> None:
        """
        Clears the cache entirely. Useful for testing or manual memory resets.
        """
        with self._lock:
            self._cache.clear()
            logger.info("Translation Cache Cleared.")

    def size(self) -> int:
        """
        Returns the number of items currently in the cache.
        Useful for health endpoints, metrics, and observability.
        """
        with self._lock:
            return len(self._cache)