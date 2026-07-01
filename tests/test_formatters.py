"""
Tests for formatters module
"""

from markrender.formatters import MarkdownFormatter
from markrender.themes import get_theme, list_themes


class TestMarkdownFormatter:
    """Test cases for MarkdownFormatter"""

    def setup_method(self):
        """Setup formatter for each test"""
        theme = get_theme('github-dark')
        self.formatter = MarkdownFormatter(theme)

    def test_format_heading_levels(self):
        """Test formatting all heading levels"""
        for level in range(1, 7):
            result = self.formatter.format_heading(level, "Test")
            assert "Test" in result

    def test_format_heading_h1_has_hash(self):
        """Test H1 heading has # marker"""
        result = self.formatter.format_heading(1, "Title")
        assert "# Title" in result
        assert "Title" in result

    def test_format_heading_h2_has_double_hash(self):
        """Test H2 heading has ## marker"""
        result = self.formatter.format_heading(2, "Subtitle")
        assert "## Subtitle" in result

    def test_format_heading_h3_no_bold(self):
        """Test H3+ heading does not get bold"""
        for level in range(3, 7):
            result = self.formatter.format_heading(level, "Test")
            assert "Test" in result

    def test_format_heading_clamp_high(self):
        """Test heading level clamped at 6"""
        result = self.formatter.format_heading(10, "High")
        assert "High" in result

    def test_format_heading_clamp_low(self):
        """Test heading level clamped at 1"""
        result = self.formatter.format_heading(0, "Low")
        assert "Low" in result

    def test_format_code_block_with_language(self):
        """Test code block formatting with language"""
        code = "def hello():\n    pass"
        result = self.formatter.format_code_block(code, "python", line_numbers=True)
        assert "hello" in result
        assert "pass" in result

    def test_format_code_block_without_language(self):
        """Test code block formatting without language"""
        code = "plain text"
        result = self.formatter.format_code_block(code, "", line_numbers=False)
        assert "plain text" in result

    def test_format_code_block_line_numbers(self):
        """Test code block has line numbers when enabled"""
        code = "line1\nline2\nline3"
        result = self.formatter.format_code_block(code, "", line_numbers=True)
        assert " 1  " in result
        assert " 2  " in result
        assert " 3  " in result

    def test_format_code_block_no_line_numbers(self):
        """Test code block without line numbers"""
        code = "line1\nline2"
        result = self.formatter.format_code_block(code, "", line_numbers=False)
        assert "line1" in result
        assert "line2" in result

    def test_format_code_block_empty(self):
        """Test empty code block formatting"""
        result = self.formatter.format_code_block("", "", line_numbers=False)
        assert result is not None

    def test_format_inline_code(self):
        """Test inline code formatting"""
        result = self.formatter.format_inline_code("code")
        assert "`code`" in result

    def test_format_inline_code_empty(self):
        """Test empty inline code"""
        result = self.formatter.format_inline_code("")
        assert "``" in result

    def test_format_table(self):
        """Test table formatting"""
        rows = [
            ["Header1", "Header2"],
            ["Cell1", "Cell2"]
        ]
        result = self.formatter.format_table(rows)
        assert "Header1" in result
        assert "Cell2" in result

    def test_format_table_borders(self):
        """Test table has border characters"""
        rows = [
            ["Header1", "Header2"],
            ["Cell1", "Cell2"]
        ]
        result = self.formatter.format_table(rows)
        assert "\u250c" in result  # ┌
        assert "\u2510" in result  # ┐
        assert "\u2514" in result  # └
        assert "\u2518" in result  # ┘
        assert "\u2502" in result  # │
        assert "\u2500" in result  # ─

    def test_format_table_header_separator(self):
        """Test table has separator after header"""
        rows = [
            ["Header1", "Header2"],
            ["Cell1", "Cell2"]
        ]
        result = self.formatter.format_table(rows)
        assert "\u251c" in result  # ├
        assert "\u2524" in result  # ┤

    def test_format_table_inconsistent_columns(self):
        """Test table with inconsistent column counts"""
        rows = [
            ["A", "B", "C"],
            ["X", "Y"],
            ["1"]
        ]
        result = self.formatter.format_table(rows)
        assert "A" in result
        assert "B" in result
        assert "C" in result
        assert "X" in result
        assert "Y" in result
        assert "1" in result

    def test_format_table_single_row(self):
        """Test table with single row"""
        rows = [["Only"]]
        result = self.formatter.format_table(rows)
        assert "Only" in result

    def test_format_table_empty(self):
        """Test table with no rows"""
        result = self.formatter.format_table([])
        assert result == ""

    def test_format_list_item_unordered(self):
        """Test unordered list item formatting"""
        result = self.formatter.format_list_item("Item", ordered=False)
        assert "Item" in result

    def test_format_list_item_ordered(self):
        """Test ordered list item formatting"""
        result = self.formatter.format_list_item("Item", ordered=True, number=1)
        assert "Item" in result

    def test_format_list_item_ordered_number(self):
        """Test ordered list item shows number"""
        result = self.formatter.format_list_item("Item", ordered=True, number=5)
        assert "Item" in result
        assert "5." in result

    def test_format_list_item_indent(self):
        """Test indented list item"""
        result = self.formatter.format_list_item("Item", indent_level=2)
        assert "Item" in result

    def test_format_checkbox_checked(self):
        """Test checked checkbox formatting"""
        result = self.formatter.format_checkbox(True, "Done")
        assert "Done" in result

    def test_format_checkbox_unchecked(self):
        """Test unchecked checkbox formatting"""
        result = self.formatter.format_checkbox(False, "Todo")
        assert "Todo" in result

    def test_format_checkbox_checked_symbol(self):
        """Test checked checkbox has checked symbol"""
        result = self.formatter.format_checkbox(True, "Done")
        assert "\u2611" in result  # ☑

    def test_format_checkbox_unchecked_symbol(self):
        """Test unchecked checkbox has unchecked symbol"""
        result = self.formatter.format_checkbox(False, "Todo")
        assert "\u2610" in result  # ☐

    def test_format_blockquote(self):
        """Test blockquote formatting"""
        result = self.formatter.format_blockquote("Quote text")
        assert "Quote text" in result

    def test_format_blockquote_multiline(self):
        """Test multiline blockquote"""
        result = self.formatter.format_blockquote("Line 1\nLine 2")
        assert "Line 1" in result
        assert "Line 2" in result

    def test_format_blockquote_border(self):
        """Test blockquote has border character"""
        result = self.formatter.format_blockquote("Quote")
        assert "\u2502" in result  # │

    def test_format_link(self):
        """Test link formatting"""
        result = self.formatter.format_link("Link Text", "https://example.com")
        assert "Link Text" in result
        assert "example.com" in result

    def test_format_link_url_visible(self):
        """Test link URL is shown"""
        result = self.formatter.format_link("Click", "https://example.com")
        assert "https://example.com" in result

    def test_format_hr(self):
        """Test horizontal rule formatting"""
        result = self.formatter.format_hr()
        assert len(result) > 0
        assert "\u2500" in result  # ─

    def test_format_hr_width_respects_setting(self):
        """Test HR respects custom width"""
        import re as _re
        formatter = MarkdownFormatter(get_theme('github-dark'), width=40)
        result = formatter.format_hr()
        clean = _re.sub(r'\033\[[0-9;]*m', '', result).strip()
        dash_count = clean.count('─')
        assert dash_count == 40, f'Expected 40 dashes, got {dash_count}'

    def test_format_emoji(self):
        """Test emoji formatting"""
        result = self.formatter.format_emoji("😊")
        assert result is not None

    def test_format_alert_note(self):
        """Test formatting NOTE alert"""
        result = self.formatter.format_alert("NOTE", "This is a note")
        assert "NOTE" in result
        assert "This is a note" in result

    def test_format_alert_tip(self):
        """Test formatting TIP alert"""
        result = self.formatter.format_alert("TIP", "Helpful tip")
        assert "TIP" in result
        assert "Helpful tip" in result

    def test_format_alert_important(self):
        """Test formatting IMPORTANT alert"""
        result = self.formatter.format_alert("IMPORTANT", "Important info")
        assert "IMPORTANT" in result
        assert "Important info" in result

    def test_format_alert_warning(self):
        """Test formatting WARNING alert"""
        result = self.formatter.format_alert("WARNING", "Warning text")
        assert "WARNING" in result
        assert "Warning text" in result

    def test_format_alert_caution(self):
        """Test formatting CAUTION alert"""
        result = self.formatter.format_alert("CAUTION", "Caution text")
        assert "CAUTION" in result
        assert "Caution text" in result

    def test_format_alert_multiline(self):
        """Test formatting multi-line alert content"""
        result = self.formatter.format_alert("NOTE", "Line 1\nLine 2")
        assert "NOTE" in result
        assert "Line 1" in result
        assert "Line 2" in result

    def test_format_alert_empty_text(self):
        """Test formatting alert with no content"""
        result = self.formatter.format_alert("NOTE", "")
        assert "NOTE" in result

    def test_format_alert_border_included(self):
        """Test alert output includes border characters"""
        result = self.formatter.format_alert("WARNING", "test")
        assert "│" in result

    def test_format_alert_colored_label(self):
        """Test all alert types produce colored labels"""
        for alert in ("NOTE", "TIP", "IMPORTANT", "WARNING", "CAUTION"):
            result = self.formatter.format_alert(alert, "content")
            assert alert in result

    def test_format_all_themes_heading(self):
        """Test heading across all themes"""
        for theme_name in list_themes():
            theme = get_theme(theme_name)
            formatter = MarkdownFormatter(theme)
            for level in range(1, 7):
                result = formatter.format_heading(level, "Test")
                assert "Test" in result

    def test_format_all_themes_table(self):
        """Test table across all themes"""
        rows = [["A", "B"], ["1", "2"]]
        for theme_name in list_themes():
            theme = get_theme(theme_name)
            formatter = MarkdownFormatter(theme)
            result = formatter.format_table(rows)
            assert "A" in result
            assert "1" in result

    def test_format_all_themes_code_block(self):
        """Test code block across all themes"""
        for theme_name in list_themes():
            theme = get_theme(theme_name)
            formatter = MarkdownFormatter(theme)
            result = formatter.format_code_block("test", "python", line_numbers=False)
            assert "test" in result

    def test_format_all_themes_blockquote(self):
        """Test blockquote across all themes"""
        for theme_name in list_themes():
            theme = get_theme(theme_name)
            formatter = MarkdownFormatter(theme)
            result = formatter.format_blockquote("Test quote")
            assert "Test quote" in result

    def test_format_all_themes_hr(self):
        """Test HR across all themes"""
        for theme_name in list_themes():
            theme = get_theme(theme_name)
            formatter = MarkdownFormatter(theme)
            result = formatter.format_hr()
            assert len(result) > 0

    def test_code_background_option(self):
        """Test code background option"""
        theme = get_theme('github-dark')
        formatter = MarkdownFormatter(theme, code_background=True)
        code = "test code"
        result = formatter.format_code_block(code, "", line_numbers=False)
        assert "test code" in result

    def test_format_image(self):
        """Test image formatting"""
        result = self.formatter.format_image("Alt", "https://example.com/img.png")
        assert "Alt" in result
        assert "img.png" in result

    def test_format_image_empty_alt(self):
        """Test image with empty alt"""
        result = self.formatter.format_image("", "img.png")
        assert "img.png" in result

    def test_format_bold(self):
        """Test bold formatting"""
        result = self.formatter.format_bold("bold")
        assert "bold" in result

    def test_format_italic(self):
        """Test italic formatting"""
        result = self.formatter.format_italic("italic")
        assert "italic" in result

    def test_format_strikethrough(self):
        """Test strikethrough formatting"""
        result = self.formatter.format_strikethrough("strike")
        assert "strike" in result
