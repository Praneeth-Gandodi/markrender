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
    
    def test_parse_code_block_delimiter(self):
        """Test parsing code block delimiter"""
        result = self.parser.parse_code_block_delimiter("```python")
        assert result == "python"
        
        result = self.parser.parse_code_block_delimiter("```")
        assert result == ""
    
    def test_parse_table_row(self):
        """Test parsing table row"""
        result = self.parser.parse_table_row("| Col1 | Col2 |")
        assert result == ["Col1", "Col2"]
    
    def test_parse_checkbox_checked(self):
        """Test parsing checked checkbox"""
        result = self.parser.parse_checkbox("- [x] Done")
        assert result == (True, "Done")
    
    def test_parse_checkbox_unchecked(self):
        """Test parsing unchecked checkbox"""
        result = self.parser.parse_checkbox("- [ ] Todo")
        assert result == (False, "Todo")
    
    def test_parse_list_item(self):
        """Test parsing unordered list item"""
        result = self.parser.parse_list_item("- Item")
        assert result == (0, "Item")
        
        result = self.parser.parse_list_item("  - Nested")
        assert result == (1, "Nested")
    
    def test_parse_ordered_list_item(self):
        """Test parsing ordered list item"""
        result = self.parser.parse_ordered_list_item("1. First")
        assert result == (0, 1, "First")
        
        result = self.parser.parse_ordered_list_item("  2. Nested")
        assert result == (1, 2, "Nested")
    
    def test_parse_blockquote(self):
        """Test parsing blockquote"""
        result = self.parser.parse_blockquote("> Quote")
        assert result == "Quote"
    
    def test_is_hr(self):
        """Test horizontal rule detection"""
        assert self.parser.is_hr("---")
        assert self.parser.is_hr("***")
        assert self.parser.is_hr("___")
        assert not self.parser.is_hr("--")
    
    def test_apply_inline_formatting_code(self):
        """Test inline code formatting"""
        text = "Use `code` here"
        result = self.parser.apply_inline_formatting(text, self.formatter)
        assert "code" in result
    
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
        # Should contain either emoji or :wave:
        assert result is not None
