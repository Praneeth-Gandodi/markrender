"""
Tests for MarkdownParser
"""

import pytest
from markrender.parser import MarkdownParser
from markrender.formatters import MarkdownFormatter
from markrender.themes import get_theme


class TestMarkdownParser:
    """Test cases for MarkdownParser"""

    def setup_method(self):
        """Setup parser for each test"""
        self.parser = MarkdownParser()
        theme = get_theme('github-dark')
        self.formatter = MarkdownFormatter(theme)

    def test_parse_heading_h1(self):
        """Test parsing H1 heading"""
        result = self.parser.parse_heading("# Title")
        assert result == (1, "Title")

    def test_parse_heading_h2(self):
        """Test parsing H2 heading"""
        result = self.parser.parse_heading("## Subtitle")
        assert result == (2, "Subtitle")

    def test_parse_heading_h6(self):
        """Test parsing H6 heading"""
        result = self.parser.parse_heading("###### Small")
        assert result == (6, "Small")

    def test_parse_heading_no_space(self):
        """Test heading without space after #"""
        result = self.parser.parse_heading("#Title")
        assert result is None

    def test_parse_heading_empty(self):
        """Test parsing heading from empty string"""
        result = self.parser.parse_heading("")
        assert result is None

    def test_parse_heading_just_hash(self):
        """Test parsing heading with just # and no text"""
        result = self.parser.parse_heading("# ")
        assert result is None

    def test_parse_code_block_delimiter(self):
        """Test parsing code block delimiter"""
        result = self.parser.parse_code_block_delimiter("```python")
        assert result == "python"

        result = self.parser.parse_code_block_delimiter("```")
        assert result == ""

    def test_parse_code_block_delimiter_empty(self):
        """Test parsing code block delimiter from empty string"""
        result = self.parser.parse_code_block_delimiter("")
        assert result is None

    def test_parse_code_block_delimiter_spaces(self):
        """Test parsing code block delimiter with trailing spaces"""
        result = self.parser.parse_code_block_delimiter("```python  ")
        assert result == "python"

    def test_parse_code_block_delimiter_indented(self):
        """Test parsing indented code block delimiter (inside lists)"""
        result = self.parser.parse_code_block_delimiter("  ```python")
        assert result == "python"

        result = self.parser.parse_code_block_delimiter("    ```")
        assert result == ""

    def test_parse_table_row(self):
        """Test parsing table row"""
        result = self.parser.parse_table_row("| Col1 | Col2 |")
        assert result == ["Col1", "Col2"]

    def test_parse_table_row_no_pipes(self):
        """Test parsing non-table line"""
        result = self.parser.parse_table_row("Col1 | Col2")
        assert result is None

    def test_parse_table_row_empty(self):
        """Test parsing table row from empty string"""
        result = self.parser.parse_table_row("")
        assert result is None

    def test_parse_table_separator_row(self):
        """Test separator row detection"""
        cells = self.parser.parse_table_row("|---|:---:|---:|")
        assert cells is not None
        assert self.parser.is_separator_row(cells) is True

    def test_parse_table_data_not_separator(self):
        """Test that data cells are not mistaken for separators"""
        cells = self.parser.parse_table_row("| --- | a |")
        assert cells is not None
        assert self.parser.is_separator_row(cells) is False

    def test_is_separator_row_empty(self):
        """Test separator detection with empty input"""
        assert self.parser.is_separator_row([]) is False
        assert self.parser.is_separator_row(None) is False

    def test_parse_checkbox_checked(self):
        """Test parsing checked checkbox"""
        result = self.parser.parse_checkbox("- [x] Done")
        assert result == (True, "Done")

    def test_parse_checkbox_unchecked(self):
        """Test parsing unchecked checkbox"""
        result = self.parser.parse_checkbox("- [ ] Todo")
        assert result == (False, "Todo")

    def test_parse_checkbox_capital_x(self):
        """Test parsing checkbox with capital X"""
        result = self.parser.parse_checkbox("- [X] Done")
        assert result == (True, "Done")

    def test_parse_checkbox_empty(self):
        """Test parsing checkbox from empty string"""
        result = self.parser.parse_checkbox("")
        assert result is None

    def test_parse_checkbox_invalid(self):
        """Test parsing invalid checkbox format"""
        result = self.parser.parse_checkbox("- [invalid] text")
        assert result is None

    def test_parse_list_item(self):
        """Test parsing unordered list item"""
        result = self.parser.parse_list_item("- Item")
        assert result == (0, "Item")

        result = self.parser.parse_list_item("  - Nested")
        assert result == (1, "Nested")

    def test_parse_list_item_empty(self):
        """Test parsing list item from empty string"""
        result = self.parser.parse_list_item("")
        assert result is None

    def test_parse_list_item_star(self):
        """Test parsing list item with * marker"""
        result = self.parser.parse_list_item("* Item")
        assert result == (0, "Item")

    def test_parse_ordered_list_item(self):
        """Test parsing ordered list item"""
        result = self.parser.parse_ordered_list_item("1. First")
        assert result == (0, 1, "First")

        result = self.parser.parse_ordered_list_item("  2. Nested")
        assert result == (1, 2, "Nested")

    def test_parse_ordered_list_item_empty(self):
        """Test parsing ordered list item from empty string"""
        result = self.parser.parse_ordered_list_item("")
        assert result is None

    def test_parse_ordered_list_item_no_dot(self):
        """Test parsing ordered list item without dot"""
        result = self.parser.parse_ordered_list_item("1 First")
        assert result is None

    def test_parse_blockquote(self):
        """Test parsing blockquote"""
        result = self.parser.parse_blockquote("> Quote")
        assert result == "Quote"

    def test_parse_alert_note(self):
        """Test parsing NOTE alert"""
        result = self.parser.parse_alert("> [!NOTE]")
        assert result == "NOTE"

    def test_parse_alert_tip(self):
        """Test parsing TIP alert"""
        result = self.parser.parse_alert("> [!TIP]")
        assert result == "TIP"

    def test_parse_alert_important(self):
        """Test parsing IMPORTANT alert"""
        result = self.parser.parse_alert("> [!IMPORTANT]")
        assert result == "IMPORTANT"

    def test_parse_alert_warning(self):
        """Test parsing WARNING alert"""
        result = self.parser.parse_alert("> [!WARNING]")
        assert result == "WARNING"

    def test_parse_alert_caution(self):
        """Test parsing CAUTION alert"""
        result = self.parser.parse_alert("> [!CAUTION]")
        assert result == "CAUTION"

    def test_parse_alert_no_space_after_bracket(self):
        """Test alert with extra spaces"""
        result = self.parser.parse_alert(">  [!NOTE]")
        assert result == "NOTE"

    def test_parse_alert_invalid_type(self):
        """Test alert with invalid type returns None"""
        result = self.parser.parse_alert("> [!DANGER]")
        assert result is None

    def test_parse_alert_regular_blockquote(self):
        """Test regular blockquote doesn't trigger alert"""
        result = self.parser.parse_alert("> Regular text")
        assert result is None

    def test_parse_alert_empty(self):
        """Test empty string doesn't match alert"""
        result = self.parser.parse_alert("")
        assert result is None

    def test_parse_blockquote_empty(self):
        """Test parsing blockquote from empty string"""
        result = self.parser.parse_blockquote("")
        assert result is None

    def test_parse_blockquote_no_space(self):
        """Test parsing blockquote without space after > returns None"""
        result = self.parser.parse_blockquote(">Quote")
        assert result is None

    def test_is_hr(self):
        """Test horizontal rule detection"""
        assert self.parser.is_hr("---")
        assert self.parser.is_hr("***")
        assert self.parser.is_hr("___")
        assert not self.parser.is_hr("--")
        assert not self.parser.is_hr("")
        assert not self.parser.is_hr("----a")

    def test_apply_inline_formatting_image(self):
        """Test image formatting"""
        text = "![Alt text](image.png)"
        result = self.parser.apply_inline_formatting(text, self.formatter)
        assert "Alt text" in result
        assert "image.png" in result

    def test_apply_inline_formatting_image_empty_alt(self):
        """Test image with empty alt text"""
        text = "![](image.png)"
        result = self.parser.apply_inline_formatting(text, self.formatter)
        assert "image.png" in result

    def test_apply_inline_formatting_code(self):
        """Test inline code formatting"""
        text = "Use `code` here"
        result = self.parser.apply_inline_formatting(text, self.formatter)
        assert "`code`" in result or "code" in result

    def test_apply_inline_formatting_code_no_spaces(self):
        """Test inline code adjacent to text"""
        text = "before`code`after"
        result = self.parser.apply_inline_formatting(text, self.formatter)
        assert result is not None

    def test_apply_inline_formatting_bold(self):
        """Test bold formatting"""
        text = "This is **bold**"
        result = self.parser.apply_inline_formatting(text, self.formatter)
        assert "bold" in result

    def test_apply_inline_formatting_italic(self):
        """Test italic formatting"""
        text = "This is *italic*"
        result = self.parser.apply_inline_formatting(text, self.formatter)
        assert "italic" in result

    def test_apply_inline_formatting_bold_and_italic(self):
        """Test bold and italic in same line"""
        text = "**Bold** and *italic*"
        result = self.parser.apply_inline_formatting(text, self.formatter)
        assert "Bold" in result
        assert "italic" in result

    def test_apply_inline_formatting_strikethrough(self):
        """Test strikethrough formatting"""
        text = "This is ~~strikethrough~~"
        result = self.parser.apply_inline_formatting(text, self.formatter)
        assert "strikethrough" in result

    def test_apply_inline_formatting_link(self):
        """Test link formatting"""
        text = "[Link](https://example.com)"
        result = self.parser.apply_inline_formatting(text, self.formatter)
        assert "Link" in result
        assert "example.com" in result

    def test_apply_inline_formatting_emoji(self):
        """Test emoji formatting"""
        text = "Hello :wave:"
        result = self.parser.apply_inline_formatting(text, self.formatter)
        assert result is not None

    def test_apply_inline_formatting_multiple(self):
        """Test multiple inline formats together"""
        text = "**Bold** `code` *italic* [link](url)"
        result = self.parser.apply_inline_formatting(text, self.formatter)
        assert result is not None

    def test_apply_inline_formatting_empty(self):
        """Test inline formatting of empty string"""
        result = self.parser.apply_inline_formatting("", self.formatter)
        assert result == ""


