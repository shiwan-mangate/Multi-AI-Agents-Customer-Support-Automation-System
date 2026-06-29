import pytest
from unittest.mock import patch, MagicMock
from layer_3.translation.helsinki_translator import HelsinkiTranslator
from layer_3.schemas.translation_result import TranslationResult

class TestHelsinkiTranslator:

    @pytest.fixture
    def mock_env(self):
        """Mocks the HuggingFace tokenizer and model to keep tests fast."""
        with patch('translation.helsinki_translator.ModelLoader') as MockLoader:
            loader_instance = MockLoader.return_value
            mock_tokenizer = MagicMock()
            mock_model = MagicMock()
            
            # Setup default generation behavior
            mock_model.generate.return_value = [["mock_token"]]
            loader_instance.get_model.return_value = (mock_tokenizer, mock_model)
            
            yield loader_instance, mock_tokenizer, mock_model

    # Test 1 & 2 — Empty String and Whitespace
    def test_empty_string(self, mock_env):
        translator = HelsinkiTranslator()
        result = translator.translate("", "hi")
        
        assert result.translated_text == ""
        assert result.translation_success is True

    def test_whitespace_only(self, mock_env):
        translator = HelsinkiTranslator()
        result = translator.translate("     ", "hi")
        
        assert result.translated_text == "     "
        assert result.translation_success is True

    # Test 3, 4, 5, 6, 7 — Standard Translations
    def test_translations(self, mock_env):
        loader, tokenizer, model = mock_env
        translator = HelsinkiTranslator()
        
        test_cases = [
            ("hi", "नमस्ते, आप कैसे हैं?", "Hello, how are you?"),
            ("hi", "मेरा ऑर्डर अभी तक नहीं आया है", "My order has not arrived yet."),
            ("es", "Hola, necesito ayuda con mi pedido", "Hello, I need help with my order"),
            ("fr", "Bonjour, où est ma commande ?", "Hello, where is my order?"),
            ("ar", "أين طلبي؟", "Where is my order?")
        ]
        
        for lang, input_text, expected_output in test_cases:
            # Configure mock to return the expected output for this test case
            tokenizer.decode.return_value = expected_output
            
            result = translator.translate(input_text, lang)
            
            assert result.translated_text == expected_output
            assert result.translation_success is True
            assert result.source_language == lang

    # Test 8 — Placeholder Preservation
    def test_placeholder_preservation(self, mock_env):
        _, tokenizer, _ = mock_env
        translator = HelsinkiTranslator()
        
        expected_translation = "Where is my order __ORDER_ID_1__ ?"
        tokenizer.decode.return_value = expected_translation
        
        result = translator.translate("मेरा ऑर्डर __ORDER_ID_1__ कहाँ है?", "hi")
        assert "__ORDER_ID_1__" in result.translated_text

    # Test 9 & 10 — TranslationResult Contract & Metadata
    def test_translation_result_contract_and_metadata(self, mock_env):
        _, tokenizer, _ = mock_env
        translator = HelsinkiTranslator()
        tokenizer.decode.return_value = "Hello"
        
        result = translator.translate("Hola", "es")
        
        assert isinstance(result, TranslationResult)
        assert result.source_language == "es"
        assert result.target_language == "en"
        assert result.translation_service == "helsinki"
        assert result.translation_success is True

    # Test 11 — Unsupported Language (Failure Fallback)
    def test_unsupported_language_fallback(self, mock_env):
        loader, _, _ = mock_env
        # Simulate ModelLoader throwing an exception for unsupported language
        loader.get_model.side_effect = ValueError("Source language 'xyz' is not supported")
        
        translator = HelsinkiTranslator()
        result = translator.translate("hello", "xyz")
        
        assert result.translation_success is False
        assert result.translated_text == "hello" # Fallback to original text

    # Test 12 — Model Cache Reuse
    def test_model_cache_reuse(self, mock_env):
        loader, tokenizer, _ = mock_env
        translator = HelsinkiTranslator()
        tokenizer.decode.return_value = "Success"
        
        translator.translate("नमस्ते", "hi")
        translator.translate("आप कैसे हैं", "hi")
        
        # The translator delegates caching to the ModelLoader.
        # We verify that it successfully asked for the model both times.
        assert loader.get_model.call_count == 2 

    # Test 13 — Customer Support Realistic Example
    def test_realistic_customer_support_example(self, mock_env):
        _, tokenizer, _ = mock_env
        translator = HelsinkiTranslator()
        
        expected = "Hello,\nMy order __ORDER_ID_1__ has not arrived yet.\nPlease help."
        tokenizer.decode.return_value = expected
        
        input_text = """
        नमस्ते,
        मेरा ऑर्डर __ORDER_ID_1__ अभी तक नहीं पहुँचा है।
        कृपया सहायता करें।
        """
        
        result = translator.translate(input_text, "hi")
        assert result.translated_text == expected

    # Test 14 — Final Smoke Test
    def test_full_smoke_test(self, mock_env):
        _, tokenizer, _ = mock_env
        translator = HelsinkiTranslator()
        tokenizer.decode.return_value = "Mocked Translation"
        
        samples = [
            ("hi", "मेरा ऑर्डर कहाँ है"),
            ("es", "¿Dónde está mi pedido?"),
            ("fr", "Où est ma commande ?"),
            ("de", "Wo ist meine Bestellung?"),
            ("ar", "أين طلبي؟")
        ]
        
        for lang, text in samples:
            result = translator.translate(text, lang)
            assert result.translation_success is True
            assert result.source_language == lang