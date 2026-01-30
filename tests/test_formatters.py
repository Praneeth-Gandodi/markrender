"""
Tests for formatters module
"""

import pytest
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
    
    def test_format_inline_code(self):
        """Test inline code formatting"""
        result = self.formatter.format_inline_code("code")
        assert "code" in result
    
    def test_format_table(self):
        """Test table formatting"""
        rows = [
            ["Header1", "Header2"],
            ["Cell1", "Cell2"]
        ]
        result = self.formatter.format_table(rows)
        assert "Header1" in result
        assert "Cell2" in result
    
    def test_format_list_item_unordered(self):
        """Test unordered list item formatting"""
        result = self.formatter.format_list_item("Item", ordered=False)
        assert "Item" in result
    
    def test_format_list_item_ordered(self):
        """Test ordered list item formatting"""
        result = self.formatter.format_list_item("Item", ordered=True, number=1)
        assert "Item" in result
    
    def test_format_checkbox_checked(self):
        """Test checked checkbox formatting"""
        result = self.formatter.format_checkbox(True, "Done")
        assert "Done" in result
    
    def test_format_checkbox_unchecked(self):
        """Test unchecked checkbox formatting"""
        result = self.formatter.format_checkbox(False, "Todo")
        assert "Todo" in result
    
    def test_format_blockquote(self):
        """Test blockquote formatting"""
        result = self.formatter.format_blockquote("Quote text")
        assert "Quote text" in result
    
    def test_format_link(self):
        """Test link formatting"""
        result = self.formatter.format_link("Link Text", "https://example.com")
        assert "Link Text" in result
        assert "example.com" in result
    
    def test_format_hr(self):
        """Test horizontal rule formatting"""
        result = self.formatter.format_hr()
        assert len(result) > 0
    
    def test_format_emoji(self):
        """Test emoji formatting"""
        result = self.formatter.format_emoji("smile")
        # Should return either emoji or :smile:
        assert result is not None
    
    def test_all_themes(self):
        """Test that all themes work"""
        for theme_name in list_themes():
            theme = get_theme(theme_name)
            formatter = MarkdownFormatter(theme)
            result = formatter.format_heading(1, "Test")
            assert "Test" in result
    
    def test_code_background_option(self):
        """Test code background option"""
        theme = get_theme('github-dark')
        formatter = MarkdownFormatter(theme, code_background=True)
        code = "test code"
        result = formatter.format_code_block(code, "", line_numbers=False)
        assert "test code" in result
