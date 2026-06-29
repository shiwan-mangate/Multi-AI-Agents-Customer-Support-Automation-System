import pytest
import logging
from layer_3.protection.placeholder_manager import PlaceholderManager

class TestPlaceholderManager:

    @pytest.fixture
    def manager(self):
        return PlaceholderManager()

    # 1. Empty Input
    def test_create_placeholders_empty_text(self, manager):
        protected, rest_map = manager.create_placeholders("", {})
        assert protected == ""
        assert rest_map == {}

    # 2. No Entities
    def test_create_placeholders_no_entities(self, manager):
        text = "Hello I need help"
        protected, rest_map = manager.create_placeholders(text, {})
        assert protected == text
        assert rest_map == {}

    # 3. Order ID
    def test_single_order_id_placeholder(self, manager):
        text = "Refund ORD-12345"
        entities = {"ORD-12345": "ORDER_ID"}
        protected, rest_map = manager.create_placeholders(text, entities)
        
        assert protected == "Refund __ORDER_ID_1__"
        assert rest_map == {"__ORDER_ID_1__": "ORD-12345"}

    # 4. Multiple Same-Type Entities
    def test_multiple_order_ids(self, manager):
        text = "ORD-111 ORD-222 ORD-333"
        entities = {"ORD-111": "ORDER_ID", "ORD-222": "ORDER_ID", "ORD-333": "ORDER_ID"}
        protected, rest_map = manager.create_placeholders(text, entities)
        
        assert "__ORDER_ID_1__" in protected
        assert "__ORDER_ID_2__" in protected
        assert "__ORDER_ID_3__" in protected
        assert len(rest_map) == 3

    # 5. Multiple Different Types
    def test_mixed_entities(self, manager):
        text = "Order ORD-12345 Ticket TKT-999 Email john@gmail.com Refund $199.99"
        entities = {
            "ORD-12345": "ORDER_ID",
            "TKT-999": "TICKET_ID",
            "john@gmail.com": "EMAIL",
            "$199.99": "AMOUNT"
        }
        protected, rest_map = manager.create_placeholders(text, entities)
        assert len(rest_map) == 4
        assert "__ORDER_ID_1__" in protected
        assert "__TICKET_ID_1__" in protected
        assert "__EMAIL_1__" in protected
        assert "__AMOUNT_1__" in protected

    # 6. Nested Length Protection
    def test_nested_length_protection(self, manager):
        text = "ORD-123 ORD-12345"
        # EntityExtractor sorted by length handles the larger one first
        entities = {"ORD-123": "ORDER_ID", "ORD-12345": "ORDER_ID"}
        protected, _ = manager.create_placeholders(text, entities)
        
        # Verify both masked, and no weird partial replacement
        assert "__ORDER_ID_1__" in protected
        assert "__ORDER_ID_2__" in protected
        assert "ORD-12345" not in protected
        assert "ORD-123" not in protected

    # 7-10. Email, URL, Amount, Phone
    def test_email_placeholder(self, manager):
        text = "john@gmail.com"
        protected, _ = manager.create_placeholders(text, {"john@gmail.com": "EMAIL"})
        assert protected == "__EMAIL_1__"

    def test_url_placeholder(self, manager):
        text = "https://openai.com"
        protected, _ = manager.create_placeholders(text, {"https://openai.com": "URL"})
        assert protected == "__URL_1__"

    def test_amount_placeholder(self, manager):
        text = "$199.99"
        protected, _ = manager.create_placeholders(text, {"$199.99": "AMOUNT"})
        assert protected == "__AMOUNT_1__"

    def test_phone_placeholder(self, manager):
        text = "+1 555 111 2222"
        protected, _ = manager.create_placeholders(text, {"+1 555 111 2222": "PHONE"})
        assert protected == "__PHONE_1__"

    # 11. Restore Single
    def test_restore_single_placeholder(self, manager):
        text = "Refund __ORDER_ID_1__"
        rest_map = {"__ORDER_ID_1__": "ORD-12345"}
        restored = manager.restore_placeholders(text, rest_map)
        assert restored == "Refund ORD-12345"

    # 12. Restore Multiple
    def test_restore_multiple_placeholders(self, manager):
        text = "Order __ORDER_ID_1__ Email __EMAIL_1__ Amount __AMOUNT_1__"
        rest_map = {
            "__ORDER_ID_1__": "ORD-12345",
            "__EMAIL_1__": "john@gmail.com",
            "__AMOUNT_1__": "$199.99"
        }
        restored = manager.restore_placeholders(text, rest_map)
        assert "ORD-12345" in restored
        assert "john@gmail.com" in restored
        assert "$199.99" in restored

    # 13. Round Trip
    def test_round_trip_protection(self, manager):
        original = "Order ORD-12345 Email john@gmail.com Refund $199.99"
        entities = {"ORD-12345": "ORDER_ID", "john@gmail.com": "EMAIL", "$199.99": "AMOUNT"}
        
        protected, rest_map = manager.create_placeholders(original, entities)
        restored = manager.restore_placeholders(protected, rest_map)
        
        assert restored == original

    # 14. Missing Placeholder Detection (with logging check)
    def test_missing_placeholder_warning(self, manager, caplog):
        with caplog.at_level(logging.WARNING):
            text = "Pedido eliminado"
            rest_map = {"__ORDER_ID_1__": "ORD-12345"}
            
            restored = manager.restore_placeholders(text, rest_map)
            
            assert "Translation anomaly" in caplog.text
            assert restored == "Pedido eliminado"

    # 15. Partial Placeholder Missing
    def test_partial_placeholder_missing(self, manager, caplog):
        with caplog.at_level(logging.WARNING):
            text = "Pedido __ORDER_ID_1__ \n Correo eliminado"
            rest_map = {
                "__ORDER_ID_1__": "ORD-12345",
                "__EMAIL_1__": "john@gmail.com"
            }
            
            restored = manager.restore_placeholders(text, rest_map)
            
            assert "Translation anomaly" in caplog.text
            assert "ORD-12345" in restored
            assert "__EMAIL_1__" not in restored

    # 16. Large Real Ticket
    def test_large_real_ticket(self, manager):
        original = """
        Hello,
        My order ORD-12345 has not arrived.
        Ticket TKT-999
        Tracking TRK-5555
        Please contact me at john@gmail.com
        Refund amount $149.99
        Website: https://company.com/refund
        """
        entities = {
            "ORD-12345": "ORDER_ID", "TKT-999": "TICKET_ID", 
            "TRK-5555": "TRACKING_ID", "john@gmail.com": "EMAIL", 
            "$149.99": "AMOUNT", "https://company.com/refund": "URL"
        }
        
        protected, rest_map = manager.create_placeholders(original, entities)
        assert len(rest_map) == 6
        
        restored = manager.restore_placeholders(protected, rest_map)
        assert restored == original