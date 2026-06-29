import pytest
import threading
from layer_3.translation.translation_cache import TranslationCache
from layer_3.schemas.translation_result import TranslationResult

class TestTranslationCache:

    @pytest.fixture(autouse=True)
    def clean_cache(self):
        """Fixture to ensure the cache is completely empty before every test."""
        cache = TranslationCache()
        cache.clear()
        yield cache

    # Test 1 — Singleton Validation
    def test_singleton_validation(self):
        cache1 = TranslationCache()
        cache2 = TranslationCache()
        assert cache1 is cache2

    # Test 2 — Empty Cache Miss
    def test_empty_cache_miss(self, clean_cache):
        result = clean_cache.get(text="Hello", source_language="en", target_language="fr")
        assert result is None

    # Test 3 & 4 — Empty Text & Whitespace Lookup
    def test_empty_text_lookup(self, clean_cache):
        result = clean_cache.get(text="", source_language="hi", target_language="en")
        assert result is None

    def test_whitespace_lookup(self, clean_cache):
        result = clean_cache.get(text="     ", source_language="hi", target_language="en")
        assert result is None

    # Test 5 & 6 — Store Translation & Cache Hit
    def test_store_and_hit_translation(self, clean_cache):
        translation = TranslationResult(
            translated_text="Hello",
            source_language="hi",
            target_language="en",
            translation_service="helsinki",
            translation_success=True
        )
        
        clean_cache.set(text="नमस्ते", source_language="hi", target_language="en", translation_result=translation)
        
        result = clean_cache.get(text="नमस्ते", source_language="hi", target_language="en")
        assert result is not None
        assert result.translated_text == "Hello"

    # Test 7 — Verify Returned Object
    def test_verify_returned_object(self, clean_cache):
        translation = TranslationResult(
            translated_text="Hello",
            source_language="hi",
            target_language="en",
            translation_service="helsinki",
            translation_success=True
        )
        clean_cache.set("नमस्ते", "hi", "en", translation)
        
        result = clean_cache.get("नमस्ते", "hi", "en")
        assert isinstance(result, TranslationResult)

    # Test 8 — Different Language Pair
    def test_different_language_pair(self, clean_cache):
        translation = TranslationResult(
            translated_text="Bonjour",
            source_language="en",
            target_language="fr",
            translation_service="helsinki",
            translation_success=True
        )
        clean_cache.set("Hello", "en", "fr", translation)
        
        result = clean_cache.get("Hello", "en", "fr")
        assert result.translated_text == "Bonjour"

    # Test 9 — Same Text Different Target
    def test_same_text_different_target(self, clean_cache):
        fr_result = TranslationResult(translated_text="Bonjour", source_language="en", target_language="fr", translation_service="helsinki", translation_success=True)
        es_result = TranslationResult(translated_text="Hola", source_language="en", target_language="es", translation_service="helsinki", translation_success=True)
        
        clean_cache.set("Hello", "en", "fr", fr_result)
        clean_cache.set("Hello", "en", "es", es_result)
        
        assert clean_cache.get("Hello", "en", "fr").translated_text == "Bonjour"
        assert clean_cache.get("Hello", "en", "es").translated_text == "Hola"

    # Test 10 — Same Text Different Source Language
    def test_same_text_different_source(self, clean_cache):
        hi_translation = TranslationResult(translated_text="Hello", source_language="hi", target_language="en", translation_service="helsinki", translation_success=True)
        es_translation = TranslationResult(translated_text="Hello", source_language="es", target_language="en", translation_service="helsinki", translation_success=True)
        
        clean_cache.set("hola", "es", "en", es_translation)
        clean_cache.set("hola", "hi", "en", hi_translation)
        
        assert clean_cache.size() == 2

    # Test 11 & 12 — SHA256 Key Consistency & Difference
    def test_sha256_key_generation(self, clean_cache):
        key1 = clean_cache._generate_key("Hello", "en", "fr")
        key2 = clean_cache._generate_key("Hello", "en", "fr")
        key3 = clean_cache._generate_key("Hello", "en", "es")
        
        assert key1 == key2
        assert key1 != key3

    # Test 13 — Clear Cache
    def test_clear_cache(self, clean_cache):
        translation = TranslationResult(translated_text="Hello", source_language="hi", target_language="en", translation_service="helsinki", translation_success=True)
        clean_cache.set("नमस्ते", "hi", "en", translation)
        
        assert clean_cache.get("नमस्ते", "hi", "en") is not None
        
        clean_cache.clear()
        assert clean_cache.get("नमस्ते", "hi", "en") is None

    # Test 14 — Ignore Invalid Store
    def test_ignore_invalid_store(self, clean_cache):
        # Pass None intentionally to trigger the guard clause
        clean_cache.set(text="", source_language="hi", target_language="en", translation_result=None)
        
        result = clean_cache.get("", "hi", "en")
        assert result is None

    # Test 15 — Overwrite Existing Entry
    def test_overwrite_existing_entry(self, clean_cache):
        first = TranslationResult(translated_text="Hello", source_language="hi", target_language="en", translation_service="helsinki", translation_success=True)
        second = TranslationResult(translated_text="Greetings", source_language="hi", target_language="en", translation_service="helsinki", translation_success=True)
        
        clean_cache.set("नमस्ते", "hi", "en", first)
        clean_cache.set("नमस्ते", "hi", "en", second)
        
        result = clean_cache.get("नमस्ते", "hi", "en")
        assert result.translated_text == "Greetings"

    # Test 16 — Thread Safety Stress Test
    def test_thread_safety_stress(self, clean_cache):
        translation = TranslationResult(translated_text="Hello", source_language="hi", target_language="en", translation_service="helsinki", translation_success=True)
        results = []

        def worker():
            clean_cache.set("नमस्ते", "hi", "en", translation)
            res = clean_cache.get("नमस्ते", "hi", "en")
            if res:
                results.append(res.translated_text)

        threads = []
        for _ in range(20):
            t = threading.Thread(target=worker)
            threads.append(t)
            t.start()

        for t in threads:
            t.join()

        assert len(results) == 20
        assert all(text == "Hello" for text in results)

    # Test 17 — Full Smoke Test
    def test_full_smoke_test(self, clean_cache):
        samples = [
            ("नमस्ते", "hi", "en", "Hello"),
            ("Hola", "es", "en", "Hello"),
            ("Bonjour", "fr", "en", "Hello"),
            ("Hallo", "de", "en", "Hello"),
        ]

        for text, source, target, translated in samples:
            result_obj = TranslationResult(
                translated_text=translated,
                source_language=source,
                target_language=target,
                translation_service="helsinki",
                translation_success=True
            )
            clean_cache.set(text, source, target, result_obj)

        for text, source, target, expected in samples:
            result = clean_cache.get(text, source, target)
            assert result is not None
            assert result.translated_text == expected
            assert clean_cache.size() == len(samples)