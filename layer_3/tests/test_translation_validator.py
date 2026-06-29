import pytest
from layer_3.translation.translation_validator import TranslationValidator

class TestTranslationValidator:

    @pytest.fixture
    def validator(self):
        return TranslationValidator()

    # Test 1 — Empty Original Text
    def test_empty_original_text(self, validator):
        assert validator.validate(original_text="", translated_text="") is True

    # Test 2 — Empty Original With Spaces
    def test_empty_original_with_spaces(self, validator):
        assert validator.validate(original_text="     ", translated_text="") is True

    # Test 3 — Normal Translation
    def test_normal_translation(self, validator):
        assert validator.validate(original_text="नमस्ते", translated_text="Hello") is True

    # Test 4 — Empty Translation
    def test_empty_translation(self, validator):
        assert validator.validate(original_text="नमस्ते", translated_text="") is False

    # Test 5 — Whitespace Translation
    def test_whitespace_translation(self, validator):
        assert validator.validate(original_text="नमस्ते", translated_text="     ") is False

    # Test 6 — Entity Placeholder Preserved
    def test_entity_placeholder_preserved(self, validator):
        assert validator.validate(
            original_text="Order __ORDER_ID_1__ not delivered", 
            translated_text="Order __ORDER_ID_1__ not delivered"
        ) is True

    # Test 7 — Entity Placeholder Lost
    def test_entity_placeholder_lost(self, validator):
        assert validator.validate(
            original_text="Order __ORDER_ID_1__ not delivered", 
            translated_text="Order not delivered"
        ) is False

    # Test 8 — Placeholder Corrupted
    def test_placeholder_corrupted(self, validator):
        assert validator.validate(
            original_text="Order __ORDER_ID_1__ not delivered", 
            translated_text="Order __ORDER__ not delivered"
        ) is False

    # Test 9 — Multiple Placeholders Preserved
    def test_multiple_placeholders_preserved(self, validator):
        assert validator.validate(
            original_text="Order __ORDER_ID_1__ Email __EMAIL_1__", 
            translated_text="Order __ORDER_ID_1__ Email __EMAIL_1__"
        ) is True

    # Test 10 — One Placeholder Missing
    def test_one_placeholder_missing(self, validator):
        assert validator.validate(
            original_text="Order __ORDER_ID_1__ Email __EMAIL_1__", 
            translated_text="Order __ORDER_ID_1__"
        ) is False

    # Test 11 — Format Placeholder Preserved
    def test_format_placeholder_preserved(self, validator):
        assert validator.validate(
            original_text="Hello __FMT_BOLD_1__", 
            translated_text="Hello __FMT_BOLD_1__"
        ) is True

    # Test 12 — Format Placeholder Lost
    def test_format_placeholder_lost(self, validator):
        assert validator.validate(
            original_text="Hello __FMT_BOLD_1__", 
            translated_text="Hello"
        ) is False

    # Test 13 — Multiple Format Placeholders
    def test_multiple_format_placeholders(self, validator):
        assert validator.validate(
            original_text="__FMT_BOLD_1__ __FMT_LINK_1__", 
            translated_text="__FMT_BOLD_1__ __FMT_LINK_1__"
        ) is True

    # Test 14 — Small Text Normal Length
    def test_small_text_normal_length(self, validator):
        assert validator.validate(original_text="Hello", translated_text="Bonjour") is True

    # Test 15 — Small Text Massive Expansion
    def test_small_text_massive_expansion(self, validator):
        assert validator.validate(original_text="Hello", translated_text="A" * 101) is False

    # Test 16 — Large Text Reasonable Expansion
    def test_large_text_reasonable_expansion(self, validator):
        assert validator.validate(original_text="A" * 100, translated_text="B" * 250) is True

    # Test 17 — Large Text Excessive Expansion
    def test_large_text_excessive_expansion(self, validator):
        assert validator.validate(original_text="A" * 100, translated_text="B" * 400) is False

    # Test 18 — Long Text Truncated
    def test_long_text_truncated(self, validator):
        assert validator.validate(original_text="A" * 200, translated_text="ok") is False

    # Test 19 — Long Text Minimum Threshold Pass
    def test_long_text_minimum_threshold_pass(self, validator):
        assert validator.validate(original_text="A" * 200, translated_text="B" * 40) is True

    # Test 20 — Realistic Customer Support Message
    def test_realistic_customer_support_message(self, validator):
        original = "\nHello,\nYour order __ORDER_ID_1__ has not been delivered.\nPlease contact support at __EMAIL_1__.\nThank you.\n"
        translated = "\nBonjour,\nVotre commande __ORDER_ID_1__ n'a pas été livrée.\nVeuillez contacter __EMAIL_1__.\nMerci.\n"
        assert validator.validate(original_text=original, translated_text=translated) is True

    # Test 21 — Realistic Placeholder Loss
    def test_realistic_placeholder_loss(self, validator):
        original = "\nOrder __ORDER_ID_1__\nEmail __EMAIL_1__\n"
        translated = "\nCommande\nEmail\n"
        assert validator.validate(original_text=original, translated_text=translated) is False

    # Test 22 — Mixed Entity + Format Placeholders
    def test_mixed_entity_and_format_placeholders(self, validator):
        original = "\n__ORDER_ID_1__\n__EMAIL_1__\n__FMT_LINK_1__\n__FMT_BOLD_1__\n"
        translated = "\n__ORDER_ID_1__\n__EMAIL_1__\n__FMT_LINK_1__\n__FMT_BOLD_1__\n"
        assert validator.validate(original_text=original, translated_text=translated) is True

    # Final Smoke Test
    def test_final_smoke_test(self, validator):
        test_cases = [
            ("Hello", "Bonjour", True),
            ("Order __ORDER_ID_1__", "Order __ORDER_ID_1__", True),
            ("Order __ORDER_ID_1__", "Order", False),
            ("Hello", "", False),
            ("A"*100, "B"*400, False),
            ("A"*200, "ok", False),
        ]
        
        for original, translated, expected_result in test_cases:
            assert validator.validate(
                original_text=original, 
                translated_text=translated
            ) is expected_result