import pytest
import logging
from layer_3.protection.format_protector import FormatProtector

class TestFormatProtector:

    @pytest.fixture
    def protector(self):
        return FormatProtector()

    # 1. Empty Input
    def test_protect_empty_text(self, protector):
        protected_text, format_map = protector.protect_formats("")
        assert protected_text == ""
        assert format_map == {}

    # 2. No Formatting
    def test_protect_plain_text(self, protector):
        text = "Hello world"
        protected_text, format_map = protector.protect_formats(text)
        assert protected_text == text
        assert format_map == {}

    # 3. Markdown Link
    def test_protect_markdown_link(self, protector):
        text = "[Track Order](https://company.com)"
        protected_text, format_map = protector.protect_formats(text)
        assert "__LINK_1__" in protected_text
        assert len(format_map) == 1

    # 4. Multiple Links
    def test_protect_multiple_links(self, protector):
        text = "[One](https://one.com)\n\n[Two](https://two.com)"
        protected_text, format_map = protector.protect_formats(text)
        assert len(format_map) == 2
        assert "__LINK_1__" in protected_text
        assert "__LINK_2__" in protected_text

    # 5. Bold Text
    def test_protect_bold_text(self, protector):
        text = "**Important Notice**"
        protected_text, format_map = protector.protect_formats(text)
        assert "__BOLD_1__" in protected_text
        assert len(format_map) == 1

    # 6. Italic Text
    def test_protect_italic_text(self, protector):
        text = "*Important*"
        protected_text, format_map = protector.protect_formats(text)
        assert "__ITALIC_1__" in protected_text
        assert len(format_map) == 1

    # 7. Inline Code
    def test_protect_inline_code(self, protector):
        text = "Use `reset_password()`"
        protected_text, format_map = protector.protect_formats(text)
        assert "__INLINE_CODE_1__" in protected_text
        assert len(format_map) == 1

    # 8. Code Block
    def test_protect_code_block(self, protector):
        text = "```python\nprint('hello')\n```"
        protected_text, format_map = protector.protect_formats(text)
        assert "__CODE_BLOCK_1__" in protected_text
        assert len(format_map) == 1

    # 9. HTML Tag
    def test_protect_html_tag(self, protector):
        text = '<a href="https://company.com">Link</a>'
        protected_text, format_map = protector.protect_formats(text)
        assert "__HTML_1__" in protected_text

    # 10. Bullet List
    def test_protect_bullet_list(self, protector):
        text = "- refund\n- replacement"
        protected_text, format_map = protector.protect_formats(text)
        assert len(format_map) == 2
        assert "__LIST_1__" in protected_text
        assert "__LIST_2__" in protected_text

    # 11. Numbered List
    def test_protect_numbered_list(self, protector):
        text = "1. Login\n2. Reset Password"
        protected_text, format_map = protector.protect_formats(text)
        assert len(format_map) == 2

    # 12. Mixed Markdown
    def test_protect_mixed_markdown(self, protector):
        text = "**Refund Status**\n\n[Track Order](https://company.com)\n\nUse `track_order()`"
        protected_text, format_map = protector.protect_formats(text)
        assert len(format_map) == 3

    # 13. Code Block + Inline
    def test_code_block_and_inline_code(self, protector):
        text = "Use `reset_password()`\n\n```python\nprint('hello')\n```"
        protected_text, format_map = protector.protect_formats(text)
        assert any("__CODE_BLOCK_" in k for k in format_map.keys())
        assert any("__INLINE_CODE_" in k for k in format_map.keys())

    # 14. Multiple Same-Type
    def test_multiple_bold_blocks(self, protector):
        text = "**One**\n\n**Two**\n\n**Three**"
        protected_text, format_map = protector.protect_formats(text)
        assert len(format_map) == 3

    # 15. Restore Single
    def test_restore_single_format(self, protector):
        text = "__BOLD_1__"
        format_map = {"__BOLD_1__": "**Important**"}
        restored = protector.restore_formats(text, format_map)
        assert restored == "**Important**"

    # 16. Restore Multiple
    def test_restore_multiple_formats(self, protector):
        text = "__BOLD_1__\n\n__LINK_1__\n\n__INLINE_CODE_1__"
        format_map = {
            "__BOLD_1__": "**Important**",
            "__LINK_1__": "[Track](https://company.com)",
            "__INLINE_CODE_1__": "`reset()`"
        }
        restored = protector.restore_formats(text, format_map)
        assert "**Important**" in restored
        assert "[Track](https://company.com)" in restored
        assert "`reset()`" in restored

    # 17. Round Trip
    def test_round_trip_format_protection(self, protector):
        original_text = """**Refund Status**\n\n[Track Order](https://company.com)\n\nUse `track_order()`\n\n
http://googleusercontent.com/immersive_entry_chip/0
http://googleusercontent.com/immersive_entry_chip/1

This completes your **Protection Layer** sub-components. You have an `EntityExtractor` (detects data) and a `FormatProtector` (detects structure), both managed by `PlaceholderManager`. 

Now, we are ready for the grand finale of this layer: **`format_and_entity_protector.py`**. This will be the Facade that orchestrates these three parts into a single API call for the LLM pipeline. Ready?"""