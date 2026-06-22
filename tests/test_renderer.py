"""
Tests for MarkdownRenderer class
"""

import pytest
import re
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

    def test_render_empty_string(self):
        """Test rendering empty string does nothing"""
        output = StringIO()
        renderer = MarkdownRenderer(output=output)
        renderer.render("")
        renderer.finalize()
        assert output.getvalue() == ""

    def test_render_none(self):
        """Test rendering None does nothing"""
        output = StringIO()
        renderer = MarkdownRenderer(output=output)
        renderer.render(None)
        renderer.finalize()
        assert output.getvalue() == ""

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

    def test_render_code_block_all_at_once(self):
        """Test code block rendered in single chunk"""
        output = StringIO()
        renderer = MarkdownRenderer(output=output)

        renderer.render("```python\ndef hello():\n    pass\n```\n")
        renderer.finalize()

        result = output.getvalue()
        assert "hello" in result

    def test_render_code_block_split_fence(self):
        """Test code fence split across chunks"""
        output = StringIO()
        renderer = MarkdownRenderer(output=output)

        renderer.render("``")
        renderer.render("`python\n")
        renderer.render("def hello():\n")
        renderer.render("    pass\n")
        renderer.render("```\n")
        renderer.finalize()

        result = output.getvalue()
        assert "hello" in result

    def test_render_code_block_split_content(self):
        """Test code content split across chunks"""
        output = StringIO()
        renderer = MarkdownRenderer(output=output)

        renderer.render("```python\n")
        renderer.render("def hello")
        renderer.render("():\n")
        renderer.render("    pri")
        renderer.render("nt('world')\n")
        renderer.render("```\n")
        renderer.finalize()

        result = output.getvalue()
        assert "hello" in result

    def test_render_empty_code_block(self):
        """Test empty code block (no content between fences)"""
        output = StringIO()
        renderer = MarkdownRenderer(output=output)

        renderer.render("```\n")
        renderer.render("```\n")
        renderer.finalize()

        result = output.getvalue()
        assert result is not None

    def test_render_code_block_closing_in_separate_chunk(self):
        """Test code block where closing fence is a separate chunk"""
        output = StringIO()
        renderer = MarkdownRenderer(output=output)

        renderer.render("```python\n")
        renderer.render("x = 1\n")
        renderer.render("```")
        renderer.render("\n")
        renderer.render("After code\n")
        renderer.finalize()

        result = output.getvalue()
        assert "After code" in result

    def test_render_consecutive_code_blocks(self):
        """Test two code blocks back to back"""
        output = StringIO()
        renderer = MarkdownRenderer(output=output)

        renderer.render("```\nfirst\n```\n")
        renderer.render("```\nsecond\n```\n")
        renderer.finalize()

        result = output.getvalue()
        assert "first" in result
        assert "second" in result

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
        assert "Done" in result
        assert "Todo" in result

    def test_render_table(self):
        """Test rendering tables"""
        output = StringIO()
        renderer = MarkdownRenderer(output=output)

        renderer.render("| Col1 | Col2 |\n")
        renderer.render("|------|------|\n")
        renderer.render("| A    | B    |\n")
        renderer.render("\n")
        renderer.finalize()

        result = output.getvalue()
        assert "Col1" in result
        assert "Col2" in result

    def test_render_table_all_at_once(self):
        """Test table rendered in a single chunk"""
        output = StringIO()
        renderer = MarkdownRenderer(output=output)

        renderer.render("| A | B |\n|---|---|\n| 1 | 2 |\n\n")
        renderer.finalize()

        result = output.getvalue()
        assert "A" in result
        assert "1" in result

    def test_render_table_inconsistent_columns(self):
        """Test table with inconsistent column counts"""
        output = StringIO()
        renderer = MarkdownRenderer(output=output)

        renderer.render("| Col1 | Col2 | Col3 |\n")
        renderer.render("|------|------|------|\n")
        renderer.render("| A | B |\n")
        renderer.render("| X | Y | Z |\n")
        renderer.render("| 1 |\n")
        renderer.render("\n")
        renderer.finalize()

        result = output.getvalue()
        assert "Col1" in result
        assert "Col2" in result

    def test_render_table_split_across_chunks(self):
        """Test table where data arrives in multiple chunks"""
        output = StringIO()
        renderer = MarkdownRenderer(output=output)

        renderer.render("| A |")
        renderer.render(" B |\n")
        renderer.render("|---")
        renderer.render("|---|\n")
        renderer.render("| 1 |")
        renderer.render(" 2 |\n")
        renderer.render("\n")
        renderer.finalize()

        result = output.getvalue()
        assert "A" in result
        assert "1" in result

    def test_render_table_with_inline_formatting(self):
        """Test table with inline formatting in cells"""
        output = StringIO()
        renderer = MarkdownRenderer(output=output)

        renderer.render("| Feature | Status |\n")
        renderer.render("|---------|--------|\n")
        renderer.render("| **Bold** | `code` |\n")
        renderer.render("\n")
        renderer.finalize()

        result = output.getvalue()
        assert "Bold" in result
        assert "code" in result

    def test_streaming_chunks(self):
        """Test rendering with streaming chunks"""
        output = StringIO()
        renderer = MarkdownRenderer(output=output)

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

    def test_alert_note(self):
        """Test rendering NOTE alert"""
        output = StringIO()
        renderer = MarkdownRenderer(output=output)
        renderer.render("> [!NOTE]\n> This is a note\n")
        renderer.render("\n")
        renderer.finalize()
        result = output.getvalue()
        assert "NOTE" in result
        assert "This is a note" in result

    def test_alert_tip(self):
        """Test rendering TIP alert"""
        output = StringIO()
        renderer = MarkdownRenderer(output=output)
        renderer.render("> [!TIP]\n> Helpful tip here\n")
        renderer.render("\n")
        renderer.finalize()
        result = output.getvalue()
        assert "TIP" in result
        assert "Helpful tip" in result

    def test_alert_important(self):
        """Test rendering IMPORTANT alert"""
        output = StringIO()
        renderer = MarkdownRenderer(output=output)
        renderer.render("> [!IMPORTANT]\n> Important message\n")
        renderer.render("\n")
        renderer.finalize()
        result = output.getvalue()
        assert "IMPORTANT" in result
        assert "Important message" in result

    def test_alert_warning(self):
        """Test rendering WARNING alert"""
        output = StringIO()
        renderer = MarkdownRenderer(output=output)
        renderer.render("> [!WARNING]\n> Warning text\n")
        renderer.render("\n")
        renderer.finalize()
        result = output.getvalue()
        assert "WARNING" in result
        assert "Warning text" in result

    def test_alert_caution(self):
        """Test rendering CAUTION alert"""
        output = StringIO()
        renderer = MarkdownRenderer(output=output)
        renderer.render("> [!CAUTION]\n> Caution text\n")
        renderer.render("\n")
        renderer.finalize()
        result = output.getvalue()
        assert "CAUTION" in result
        assert "Caution text" in result

    def test_alert_multiline(self):
        """Test rendering multi-line alert"""
        output = StringIO()
        renderer = MarkdownRenderer(output=output)
        renderer.render("> [!NOTE]\n> Line one\n> Line two\n")
        renderer.render("\n")
        renderer.finalize()
        result = output.getvalue()
        assert "NOTE" in result
        assert "Line one" in result
        assert "Line two" in result

    def test_alert_standalone_no_content(self):
        """Test rendering alert header with no content"""
        output = StringIO()
        renderer = MarkdownRenderer(output=output)
        renderer.render("> [!NOTE]\n")
        renderer.render("\n")
        renderer.finalize()
        result = output.getvalue()
        assert "NOTE" in result

    def test_alert_with_inline_formatting(self):
        """Test alert with inline formatting"""
        output = StringIO()
        renderer = MarkdownRenderer(output=output)
        renderer.render("> [!TIP]\n> Use **bold** and *italic*\n")
        renderer.render("\n")
        renderer.finalize()
        result = output.getvalue()
        assert "TIP" in result

    def test_horizontal_rule(self):
        """Test rendering horizontal rule"""
        output = StringIO()
        renderer = MarkdownRenderer(output=output)

        renderer.render("---\n")
        renderer.finalize()

        result = output.getvalue()
        assert len(result) > 0

    def test_finalize_flushes_buffer(self):
        """Test that finalize flushes remaining buffer"""
        output = StringIO()
        renderer = MarkdownRenderer(output=output)

        renderer.render("Incomplete text")

        renderer.finalize()

        result = output.getvalue()
        assert "Incomplete" in result

    def test_finalize_flushes_incomplete_code_block(self):
        """Test that finalize renders incomplete code block"""
        output = StringIO()
        renderer = MarkdownRenderer(output=output)

        renderer.render("```python\n")
        renderer.render("print('hello')\n")
        renderer.finalize()

        result = output.getvalue()
        assert "hello" in result

    def test_finalize_flushes_incomplete_table(self):
        """Test that finalize renders incomplete table"""
        output = StringIO()
        renderer = MarkdownRenderer(output=output)

        renderer.render("| A | B |\n")
        renderer.render("|---|---|\n")
        renderer.render("| 1 | 2 |\n")
        renderer.finalize()

        result = output.getvalue()
        assert "A" in result

    def test_finalize_flushes_incomplete_blockquote(self):
        """Test that finalize renders incomplete blockquote"""
        output = StringIO()
        renderer = MarkdownRenderer(output=output)

        renderer.render("> Incomplete\n")
        renderer.render("> blockquote\n")
        renderer.finalize()

        result = output.getvalue()
        assert "Incomplete" in result

    def test_render_image_with_link(self):
        """Test rendering image followed by link"""
        output = StringIO()
        renderer = MarkdownRenderer(output=output)

        renderer.render("![icon](icon.png) and [text](url)\n")
        renderer.finalize()

        result = output.getvalue()
        assert "icon" in result
        assert "text" in result

    def test_all_themes_heading(self):
        """Test rendering headings across all themes"""
        for theme in list_themes():
            output = StringIO()
            renderer = MarkdownRenderer(theme=theme, output=output)
            renderer.render("# Title\n")
            renderer.finalize()
            assert "Title" in output.getvalue()

    def test_render_ordered_list(self):
        """Test rendering ordered list"""
        output = StringIO()
        renderer = MarkdownRenderer(output=output)

        renderer.render("1. First\n")
        renderer.render("2. Second\n")
        renderer.finalize()

        result = output.getvalue()
        assert "First" in result
        assert "Second" in result

    def test_render_nested_list(self):
        """Test rendering nested list"""
        output = StringIO()
        renderer = MarkdownRenderer(output=output)

        renderer.render("- Item\n")
        renderer.render("  - Nested\n")
        renderer.finalize()

        result = output.getvalue()
        assert "Item" in result
        assert "Nested" in result

    def test_render_code_block_in_list(self):
        """Test rendering code block inside a list item"""
        output = StringIO()
        renderer = MarkdownRenderer(output=output)

        renderer.render("- Item\n")
        renderer.render("  ```\n")
        renderer.render("  code inside list\n")
        renderer.render("  ```\n")
        renderer.render("\n")
        renderer.finalize()

        result = output.getvalue()
        assert "Item" in result
        assert "code inside list" in result

    def test_render_code_block_preserves_indentation(self):
        """Test streaming code preserves leading whitespace/indentation"""
        output = StringIO()
        renderer = MarkdownRenderer(output=output)

        renderer.render("```html\n")
        renderer.render("  <div>\n")
        renderer.render("    <p>Hello</p>\n")
        renderer.render("  </div>\n")
        renderer.render("```\n")
        renderer.render("\n")
        renderer.finalize()

        result = output.getvalue()
        clean = re.sub(r'\033\[[0-9;]*m', '', result)
        assert "  <div>" in clean
        assert "    <p>Hello</p>" in clean
        assert "  </div>" in clean

    def test_render_mixed_content(self):
        """Test rendering mixed content types"""
        output = StringIO()
        renderer = MarkdownRenderer(output=output)

        renderer.render("# Title\n\n")
        renderer.render("Text with **bold** and `code`\n\n")
        renderer.render("- List item\n\n")
        renderer.render("> Blockquote\n")
        renderer.render("---\n")
        renderer.finalize()

        result = output.getvalue()
        assert "Title" in result
        assert "bold" in result
        assert "List" in result
        assert "Blockquote" in result

    def test_render_image(self):
        """Test rendering image markdown"""
        output = StringIO()
        renderer = MarkdownRenderer(output=output)

        renderer.render("![Logo](https://example.com/logo.png)\n")
        renderer.finalize()

        result = output.getvalue()
        assert "Logo" in result
        assert "logo.png" in result or "example.com" in result

    def test_render_code_block_after_table(self):
        """Test code block following a table"""
        output = StringIO()
        renderer = MarkdownRenderer(output=output)

        renderer.render("| A | B |\n")
        renderer.render("|---|---|\n")
        renderer.render("| 1 | 2 |\n")
        renderer.render("\n")
        renderer.render("```\ncode\n```\n")
        renderer.finalize()

        result = output.getvalue()
        assert "A" in result
        assert "code" in result

    def test_render_table_after_code_block(self):
        """Test table following a code block"""
        output = StringIO()
        renderer = MarkdownRenderer(output=output)

        renderer.render("```\ncode\n```\n")
        renderer.render("\n")
        renderer.render("| A | B |\n")
        renderer.render("|---|---|\n")
        renderer.render("| 1 | 2 |\n")
        renderer.render("\n")
        renderer.finalize()

        result = output.getvalue()
        assert "A" in result
        assert "code" in result
