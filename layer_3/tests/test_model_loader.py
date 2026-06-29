import pytest
import threading
from unittest.mock import patch, MagicMock
from layer_3.translation.model_loader import ModelLoader

class TestModelLoader:

    @pytest.fixture(autouse=True)
    def reset_singleton(self):
        """Reset the singleton before each test to ensure clean state."""
        ModelLoader._instance = None
        yield


    def test_singleton_validation(self):
        loader1 = ModelLoader()
        loader2 = ModelLoader()
        assert loader1 is loader2


    def test_initial_state(self):
        loader = ModelLoader()
        assert len(loader.loaded_models) == 0


    def test_is_loaded_before_load(self):
        loader = ModelLoader()
        assert loader.is_loaded(source_language="hi", target_language="en") is False

  
    @patch("translation.model_loader.MarianMTModel.from_pretrained")
    @patch("translation.model_loader.MarianTokenizer.from_pretrained")
    def test_hindi_model_load(self, mock_tokenizer, mock_model):
        mock_tokenizer.return_value = "MockTokenizer"
        mock_model.return_value = "MockModel"
        
        loader = ModelLoader()
        tokenizer, model = loader.get_model(source_language="hi", target_language="en")
        
        assert tokenizer == "MockTokenizer"
        assert model == "MockModel"
        assert list(loader.loaded_models.keys()) == ["hi-en"]

  
    @patch("translation.model_loader.MarianMTModel.from_pretrained")
    @patch("translation.model_loader.MarianTokenizer.from_pretrained")
    def test_is_loaded_after_load(self, mock_tokenizer, mock_model):
        loader = ModelLoader()
        loader.get_model("hi", "en")
        assert loader.is_loaded("hi", "en") is True

   
    @patch("translation.model_loader.MarianMTModel.from_pretrained")
    @patch("translation.model_loader.MarianTokenizer.from_pretrained")
    def test_cache_hit_validation(self, mock_tokenizer, mock_model):
      
        mock_tokenizer.return_value = MagicMock()
        mock_model.return_value = MagicMock()
        
        loader = ModelLoader()
        tokenizer1, model1 = loader.get_model("hi", "en")
        tokenizer2, model2 = loader.get_model("hi", "en")
        
        assert tokenizer1 is tokenizer2
        assert model1 is model2
      
        assert mock_tokenizer.call_count == 1 


    @patch("translation.model_loader.MarianMTModel.from_pretrained")
    @patch("translation.model_loader.MarianTokenizer.from_pretrained")
    def test_multiple_languages(self, mock_tokenizer, mock_model):
        loader = ModelLoader()
        loader.get_model("hi", "en")
        loader.get_model("es", "en")
        loader.get_model("fr", "en")
        
        assert list(loader.loaded_models.keys()) == ['hi-en', 'es-en', 'fr-en']

    
    def test_unsupported_source_language(self):
        loader = ModelLoader()
        with pytest.raises(ValueError) as exc:
            loader.get_model("xyz", "en")
        assert "Source language 'xyz' is not supported" in str(exc.value)

    
    def test_unsupported_target_language(self):
        loader = ModelLoader()
        with pytest.raises(ValueError) as exc:
            loader.get_model("hi", "fr")
        assert "Target language 'fr' is not supported" in str(exc.value)

   
    @patch("translation.model_loader.MarianMTModel.from_pretrained")
    @patch("translation.model_loader.MarianTokenizer.from_pretrained")
    def test_cache_size_validation(self, mock_tokenizer, mock_model):
        loader = ModelLoader()
        loader.get_model("hi", "en")
        loader.get_model("hi", "en")
        loader.get_model("hi", "en")
        
        assert len(loader.loaded_models) == 1

   
    @patch("translation.model_loader.MarianMTModel.from_pretrained")
    @patch("translation.model_loader.MarianTokenizer.from_pretrained")
    def test_thread_safety_check(self, mock_tokenizer, mock_model):
        loader = ModelLoader()
        
        def worker():
            loader.get_model("hi", "en")

        threads = []
        for _ in range(10):
            t = threading.Thread(target=worker)
            threads.append(t)
            t.start()

        for t in threads:
            t.join()

        
        assert mock_model.call_count == 1
        assert list(loader.loaded_models.keys()) == ['hi-en']


    @patch("translation.model_loader.MarianMTModel.from_pretrained")
    @patch("translation.model_loader.MarianTokenizer.from_pretrained")
    def test_full_smoke_test(self, mock_tokenizer, mock_model):
        loader = ModelLoader()
        languages = ["hi", "es", "fr", "de", "ar"]
        
        for lang in languages:
            loader.get_model(lang, "en")
            assert loader.is_loaded(lang, "en") is True
            
        expected_keys = ['hi-en', 'es-en', 'fr-en', 'de-en', 'ar-en']
        assert list(loader.loaded_models.keys()) == expected_keys
        assert mock_model.call_count == 5 