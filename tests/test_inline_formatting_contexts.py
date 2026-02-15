
import pytest
from markrender.parser import MarkdownParser
from markrender.renderer import MarkdownRenderer
from markrender.formatters import MarkdownFormatter
from markrender.themes import get_theme
from io import StringIO
import re

class TestInlineFormattingContexts:
    """Test inline formatting within various contexts"""
    
    def test_inline_formatting_in_list(self):
        """Test inline formatting within list items"""
        markdown = "- Item with **bold** text"
        
        output = StringIO()
        renderer = MarkdownRenderer(output=output, force_color=True, width=80)
        renderer.render(markdown)
        renderer.finalize()
        result = output.getvalue()
        
        # Check that [bold] markup is parsed and not literal
        assert "[bold]" not in result
        # Check that ANSI code is present (indicating rich rendered it)
        # Note: Depending on terminal detection, force_color=True forces rich to output ANSI
        assert "\x1b" in result
        assert "bold" in result

    def test_inline_formatting_in_table(self):
        """Test inline formatting within table cells"""
        markdown = "| Col1 | Col2 |\n| --- | --- |\n| **Bold** | *Italic* |"
        
        output = StringIO()
        renderer = MarkdownRenderer(output=output, force_color=True, width=80)
        renderer.render(markdown)
        renderer.finalize()
        result = output.getvalue()
        
        assert "[bold]" not in result
        assert "[italic]" not in result
        assert "Bold" in result
        assert "Italic" in result
        assert "\x1b" in result
