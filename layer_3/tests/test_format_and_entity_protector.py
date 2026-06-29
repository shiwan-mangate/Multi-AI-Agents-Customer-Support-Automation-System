import pytest
from unittest.mock import patch
from layer_3.protection.format_and_entity_protector import FormatAndEntityProtector

class TestFormatAndEntityProtector:

    @pytest.fixture
    def protector(self):
        return FormatAndEntityProtector()

    # 1. Empty Text
    def test_protect_empty_text(self, protector):
        result = protector.protect("")
        assert result.original_text == ""
        assert result.protected_text == ""
        assert result.entity_count == 0
        assert result.format_count == 0

    # 2. Plain Text
    def test_protect_plain_text(self, protector):
        text = "Hello world"
        result = protector.protect(text)
        assert result.original_text == text
        assert result.entity_count == 0
        assert result.format_count == 0

    # 3. Entity Only
    def test_protect_entity_only(self, protector):
        text = "Refund ORD-12345"
        result = protector.protect(text)
        assert result.entity_count == 1
        assert result.format_count == 0
        assert "__ORDER_ID_1__" in result.protected_text

    # 4. Format Only
    def test_protect_format_only(self, protector):
        text = "**Important Notice**"
        result = protector.protect(text)
        assert result.entity_count == 0
        assert result.format_count == 1
        assert "__FMT_BOLD_1__" in result.protected_text

    # 5. Entity + Format (Orchestration Test)
    def test_protect_entity_and_format(self, protector):
        text = "**Refund Status**\n\nOrder ORD-12345\n\nEmail john@gmail.com"
        result = protector.protect(text)
        
        assert result.entity_count == 2
        assert result.format_count == 1
        assert "__ORDER_ID_1__" in result.protected_text
        assert "__EMAIL_1__" in result.protected_text
        assert "__FMT_BOLD_1__" in result.protected_text

    # 6. Restore Entity Only
    def test_restore_entity_only(self, protector):
        text = "Refund ORD-12345"
        protected = protector.protect(text)
        restored = protector.restore(protected.protected_text, protected)
        assert restored == text

    # 7. Restore Format Only
    def test_restore_format_only(self, protector):
        text = "**Important**"
        protected = protector.protect(text)
        restored = protector.restore(protected.protected_text, protected)
        assert restored == text

    # 8. Restore Mixed Content
    def test_restore_mixed_content(self, protector):
        text = "**Refund Status**\n\nOrder ORD-12345\n\nEmail john@gmail.com\n\n[Track](https://company.com)"
        protected = protector.protect(text)
        restored = protector.restore(protected.protected_text, protected)
        assert restored == text

    # 9. Round Trip Validation (The "Gold Standard" Test)
    def test_round_trip_validation(self, protector):
        original_text = """
**Refund Status**

Order ORD-12345

Ticket TKT-999

Tracking TRK-5555

Email john@gmail.com

Refund Amount $149.99

[Track Order](https://company.com)

`track_order()`
"""
        protected = protector.protect(original_text)
        restored = protector.restore(protected.protected_text, protected)
        assert restored == original_text

    # 10. Real FAQ Response
    def test_real_faq_response(self, protector):
        text = """
**Password Reset Guide**

1. Login

2. Click:

[Reset Password](https://company.com/reset)

3. Run:

`reset_password()`

```json
{
  "status": "success"
}
"""