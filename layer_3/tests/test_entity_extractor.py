import pytest
from layer_3.protection.entity_extractor import EntityExtractor

class TestEntityExtractor:

    @pytest.fixture
    def extractor(self):
        return EntityExtractor()

    # 1. Empty Input
    def test_extract_entities_empty_text(self, extractor):
        assert extractor.extract_entities("") == {}

    # 2. No Entities
    def test_extract_entities_no_entities(self, extractor):
        text = "Hello I need help with my account"
        result = extractor.extract_entities(text)
        assert result == {}

    # 3. Order ID
    def test_extract_order_id(self, extractor):
        text = "Refund order ORD-12345"
        result = extractor.extract_entities(text)
        assert result == {"ORD-12345": "ORDER_ID"}

    # 4. Multiple Order IDs
    def test_extract_multiple_order_ids(self, extractor):
        text = "ORD-111 ORD-222 ORD-333"
        result = extractor.extract_entities(text)
        assert len(result) == 3

    # 5. Ticket ID
    def test_extract_ticket_id(self, extractor):
        text = "Ticket TKT-999"
        result = extractor.extract_entities(text)
        assert result == {"TKT-999": "TICKET_ID"}

    # 6. Customer ID
    def test_extract_customer_id(self, extractor):
        text = "Customer CUS-123"
        result = extractor.extract_entities(text)
        assert result == {"CUS-123": "CUSTOMER_ID"}

    # 7. Tracking ID
    def test_extract_tracking_id(self, extractor):
        text = "Tracking TRK-55555"
        result = extractor.extract_entities(text)
        assert result == {"TRK-55555": "TRACKING_ID"}

    # 8. Email
    def test_extract_email(self, extractor):
        text = "Contact john@gmail.com"
        result = extractor.extract_entities(text)
        assert result == {"john@gmail.com": "EMAIL"}

    # 9. Multiple Emails
    def test_extract_multiple_emails(self, extractor):
        text = "john@gmail.com support@company.com"
        result = extractor.extract_entities(text)
        assert len(result) == 2

    # 10. Phone Number
    def test_extract_phone_number(self, extractor):
        text = "Call me at +1 555 111 2222"
        result = extractor.extract_entities(text)
        assert len(result) == 1
        assert "PHONE" in result.values()

    # 11. URL
    def test_extract_url(self, extractor):
        text = "Visit https://openai.com"
        result = extractor.extract_entities(text)
        assert result == {"https://openai.com": "URL"}

    # 12. WWW URL
    def test_extract_www_url(self, extractor):
        text = "Visit www.example.com"
        result = extractor.extract_entities(text)
        assert result == {"www.example.com": "URL"}

    # 13. Dollar Amount
    def test_extract_dollar_amount(self, extractor):
        text = "Refund amount is $199.99"
        result = extractor.extract_entities(text)
        assert result == {"$199.99": "AMOUNT"}

    # 14. Rupee Amount
    def test_extract_rupee_amount(self, extractor):
        text = "Refund ₹5000"
        result = extractor.extract_entities(text)
        assert result == {"₹5000": "AMOUNT"}

    # 15. Real Customer Support Message
    def test_extract_real_support_message(self, extractor):
        text = """
        Hello,
        My order ORD-12345 has not arrived.
        Ticket: TKT-999
        Tracking: TRK-7777
        Refund amount: $149.99
        Contact me at john@gmail.com
        """
        result = extractor.extract_entities(text)
        assert len(result) == 5
        assert result["ORD-12345"] == "ORDER_ID"
        assert result["TKT-999"] == "TICKET_ID"
        assert result["TRK-7777"] == "TRACKING_ID"
        assert result["$149.99"] == "AMOUNT"
        assert result["john@gmail.com"] == "EMAIL"

    # 16. Duplicate Protection
    def test_duplicate_entities_return_once(self, extractor):
        text = """
        ORD-12345
        ORD-12345
        ORD-12345
        """
        result = extractor.extract_entities(text)
        assert len(result) == 1