"""
Tests for MarkdownRenderer class
"""
import re

def strip_ansi(text):
    return re.sub(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])', '', text)

import pytest
from io import StringIO
from markrender import MarkdownRenderer
from markrender.themes import list_themes


class TestMarkdownRenderer:
    """Test cases for MarkdownRenderer"""
    
    def test_initialization_default(self):
        """Test renderer initialization with defaults"""
        renderer = MarkdownRenderer()
        assert renderer.theme_config is not None
        assert renderer.code_background == False
        assert renderer.line_numbers == True
    
    def test_initialization_custom_theme(self):
        """Test renderer initialization with custom theme"""
        for theme in list_themes():
            renderer = MarkdownRenderer(theme=theme)
            assert renderer.theme_config['name'] == theme
    
    def test_invalid_theme(self):
        """Test that invalid theme raises ValueError"""
        with pytest.raises(ValueError):
            MarkdownRenderer(theme='nonexistent-theme')
    
    def test_render_simple_text(self):
        """Test rendering simple text"""
        output = StringIO()
        renderer = MarkdownRenderer(output=output)
        renderer.render("Hello, World!\n")
        renderer.finalize()
        
        result = output.getvalue()
        assert "Hello" in result
    
    def test_render_heading(self):
        """Test rendering headings"""
        output = StringIO()
        renderer = MarkdownRenderer(output=output)
        
        renderer.render("# Heading 1\n")
        renderer.render("## Heading 2\n")
        renderer.finalize()
        
        result = output.getvalue()
        assert "Heading 1" in result
        assert "Heading 2" in result
    
    def test_render_code_block(self):
        """Test rendering code block"""
        output = StringIO()
        renderer = MarkdownRenderer(output=output)
        
        renderer.render("```python\n")
        renderer.render("def hello():\n")
        renderer.render("    print('world')\n")
        renderer.render("```\n")
        renderer.finalize()
        
        result = output.getvalue()
        assert "hello" in result
        assert "world" in result
    
    def test_render_inline_code(self):
        """Test rendering inline code"""
        output = StringIO()
        renderer = MarkdownRenderer(output=output)
        
        renderer.render("Use `code` here\n")
        renderer.finalize()
        
        result = output.getvalue()
        assert "code" in result
    
    def test_render_list(self):
        """Test rendering lists"""
        output = StringIO()
        renderer = MarkdownRenderer(output=output)
        
        renderer.render("- Item 1\n")
        renderer.render("- Item 2\n")
        renderer.finalize()
        
        result = output.getvalue()
        assert "Item 1" in result
        assert "Item 2" in result
    
    def test_render_checkbox(self):
        """Test rendering checkboxes"""
        output = StringIO()
        renderer = MarkdownRenderer(output=output)
        
        renderer.render("- [x] Done\n")
        renderer.render("- [ ] Todo\n")
        renderer.finalize()
        
        result = output.getvalue()
        assert "✅  Done" in result
        assert "⬜  Todo" in result
    
    def test_render_table(self):
        """Test rendering tables"""
        output = StringIO()
        renderer = MarkdownRenderer(output=output)
        
        renderer.render("| Col1 | Col2 |\n")
        renderer.render("|------|------|\n")
        renderer.render("| A    | B    |\n")
        renderer.render("\n")  # End table
        renderer.finalize()
        
        result = output.getvalue()
        assert "Col1" in result
        assert "Col2" in result

    def test_render_large_table(self):
        """Test rendering large tables"""
        output = StringIO()
        renderer = MarkdownRenderer(output=output, width=200)
        
        # Header
        renderer.render("| Head1 | Head2 | Head3 | Head4 | Head5 | Head6 | Head7 | Head8 | Head9 | Head10 |\n")
        renderer.render("|---|---|---|---|---|---|---|---|---|---|")
        # Body
        for i in range(20):
            renderer.render(f"| Col{i}-1 | Col{i}-2 | Col{i}-3 | Col{i}-4 | Col{i}-5 | Col{i}-6 | Col{i}-7 | Col{i}-8 | Col{i}-9 | Col{i}-10 |\n")
        renderer.render("\n")  # End table
        renderer.finalize()
        
        result = output.getvalue()
        assert "Head1" in result
        assert "Col19-10" in result
    
    def test_streaming_chunks(self):
        """Test rendering with streaming chunks"""
        output = StringIO()
        renderer = MarkdownRenderer(output=output)
        
        # Simulate streaming response
        chunks = ["# ", "Title", "\n", "Some ", "text ", "here\n"]
        for chunk in chunks:
            renderer.render(chunk)
        renderer.finalize()
        
        result = output.getvalue()
        assert "Title" in result
        assert "text" in result
    
    def test_code_background_option(self):
        """Test code_background option"""
        output = StringIO()
        renderer = MarkdownRenderer(output=output, code_background=True)
        
        renderer.render("```\ncode\n```\n")
        renderer.finalize()
        
        result = output.getvalue()
        assert "code" in result
    
    def test_line_numbers_disabled(self):
        """Test disabling line numbers"""
        output = StringIO()
        renderer = MarkdownRenderer(output=output, line_numbers=False)
        
        renderer.render("```python\ndef test():\n    pass\n```\n")
        renderer.finalize()
        
        result = output.getvalue()
        assert "test" in result
    
    def test_blockquote(self):
        """Test rendering blockquotes"""
        output = StringIO()
        renderer = MarkdownRenderer(output=output)
        
        renderer.render("> Quote line 1\n")
        renderer.render("> Quote line 2\n")
        renderer.render("\n")
        renderer.finalize()
        
        result = output.getvalue()
        assert "Quote" in result
    
    def test_horizontal_rule(self):
        """Test rendering horizontal rule"""
        output = StringIO()
        renderer = MarkdownRenderer(output=output)
        
        renderer.render("---\n")
        renderer.finalize()
        
        result = output.getvalue()
        # Should contain some separator characters
        assert len(result) > 0
    
    def test_finalize_flushes_buffer(self):
        """Test that finalize flushes remaining buffer"""
        output = StringIO()
        renderer = MarkdownRenderer(output=output)
        
        # Add text without newline
        renderer.render("Incomplete text")
        
        # Finalize should process it
        renderer.finalize()
        
        # Check output contains the text
        result = output.getvalue()
        assert "Incomplete" in result
        
    def test_render_code_block_with_leading_whitespace(self):
        """Test rendering code block with leading whitespace"""
        output = StringIO()
        renderer = MarkdownRenderer(output=output)
        
        renderer.render("  ```python\n")
        renderer.render("  def hello():\n")
        renderer.render("      print('world')\n")
        renderer.render("  ```\n")
        renderer.finalize()
        
        result = output.getvalue()
        assert "hello" in result
        assert "world" in result

    def test_render_emoji(self):
        """Test rendering emoji"""
        output = StringIO()
        renderer = MarkdownRenderer(output=output)
        
        renderer.render("Hello :wave:\n")
        renderer.finalize()
        
        result = output.getvalue()
        assert "👋" in result

    def test_render_blockquote_as_note(self):
        """Test rendering a blockquote that is a note"""
        output = StringIO()
        renderer = MarkdownRenderer(output=output)
        
        renderer.render("> [!NOTE] This is a note.\n")
        renderer.finalize()
        
        result_with_ansi = output.getvalue()
        result = strip_ansi(result_with_ansi)
        assert "NOTE: This is a note." in result # Changed expected string to match new format

        # Check that it doesn't have the blockquote border
        assert "│" not in result_with_ansi # Check original result as it has ANSI codes

    def test_render_regular_blockquote(self):
        """Test rendering a regular blockquote"""
        output = StringIO()
        renderer = MarkdownRenderer(output=output)
        
        renderer.render("> This is a quote.\n")
        renderer.finalize()
        
        result = output.getvalue()
        assert "This is a quote." in result
        # Check that it has the blockquote border
        assert "│" in result