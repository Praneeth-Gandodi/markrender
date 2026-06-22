"""
Tests for new MarkRender features
"""

import pytest
from io import StringIO
from markrender import MarkdownRenderer, register_theme


class TestHighlightSyntax:
    """Test ==highlight== syntax"""

    def test_highlight_basic(self):
        """Test basic highlight syntax"""
        output = StringIO()
        renderer = MarkdownRenderer(output=output)
        
        renderer.render("This is ==highlighted== text\n")
        renderer.finalize()
        
        result = output.getvalue()
        assert "highlighted" in result

    def test_highlight_multiple(self):
        """Test multiple highlights in same line"""
        output = StringIO()
        renderer = MarkdownRenderer(output=output)
        
        renderer.render("First ==highlight1== and ==highlight2==\n")
        renderer.finalize()
        
        result = output.getvalue()
        assert "highlight1" in result
        assert "highlight2" in result

    def test_highlight_with_bold(self):
        """Test highlight combined with bold"""
        output = StringIO()
        renderer = MarkdownRenderer(output=output)
        
        renderer.render("==**bold highlight**==\n")
        renderer.finalize()
        
        result = output.getvalue()
        assert "bold highlight" in result


class TestNestedLists:
    """Test nested list support"""

    def test_nested_unordered_lists(self):
        """Test nested unordered lists"""
        output = StringIO()
        renderer = MarkdownRenderer(output=output)
        
        renderer.render("- Item 1\n")
        renderer.render("  - Nested item 1\n")
        renderer.render("  - Nested item 2\n")
        renderer.render("- Item 2\n")
        renderer.finalize()
        
        result = output.getvalue()
        assert "Item 1" in result
        assert "Nested item 1" in result
        assert "Nested item 2" in result
        assert "Item 2" in result

    def test_nested_ordered_lists(self):
        """Test nested ordered lists"""
        output = StringIO()
        renderer = MarkdownRenderer(output=output)
        
        renderer.render("1. First\n")
        renderer.render("   1. Nested first\n")
        renderer.render("   2. Nested second\n")
        renderer.render("2. Second\n")
        renderer.finalize()
        
        result = output.getvalue()
        assert "First" in result
        assert "Nested first" in result
        assert "Second" in result

    def test_mixed_nested_lists(self):
        """Test mixed ordered and unordered nested lists"""
        output = StringIO()
        renderer = MarkdownRenderer(output=output)
        
        renderer.render("1. Ordered\n")
        renderer.render("   - Unordered nested\n")
        renderer.render("2. Second\n")
        renderer.finalize()
        
        result = output.getvalue()
        assert "Ordered" in result
        assert "Unordered nested" in result
        assert "Second" in result


class TestProgressBars:
    """Test progress bar task items"""

    def test_progress_bar_basic(self):
        """Test basic progress bar"""
        output = StringIO()
        renderer = MarkdownRenderer(output=output)
        
        renderer.render("- [50%] Half done\n")
        renderer.finalize()
        
        result = output.getvalue()
        assert "50%" in result
        assert "Half done" in result

    def test_progress_bar_complete(self):
        """Test 100% progress bar"""
        output = StringIO()
        renderer = MarkdownRenderer(output=output)
        
        renderer.render("- [100%] Complete!\n")
        renderer.finalize()
        
        result = output.getvalue()
        assert "100%" in result
        assert "Complete!" in result
        assert "✅" in result

    def test_progress_bar_various_percentages(self):
        """Test various progress percentages"""
        output = StringIO()
        renderer = MarkdownRenderer(output=output)
        
        renderer.render("- [0%] Not started\n")
        renderer.render("- [25%] Started\n")
        renderer.render("- [75%] Almost done\n")
        renderer.render("- [100%] Done\n")
        renderer.finalize()
        
        result = output.getvalue()
        assert "0%" in result
        assert "25%" in result
        assert "75%" in result
        assert "100%" in result


class TestImagePlaceholders:
    """Test image placeholder rendering"""

    def test_image_basic(self):
        """Test basic image placeholder"""
        output = StringIO()
        renderer = MarkdownRenderer(output=output)
        
        renderer.render("Check this: ![Alt text](https://example.com/image.png)\n")
        renderer.finalize()
        
        result = output.getvalue()
        assert "Alt text" in result
        assert "example.com" in result

    def test_image_no_alt(self):
        """Test image without alt text"""
        output = StringIO()
        renderer = MarkdownRenderer(output=output)
        
        renderer.render("![](https://example.com/img.jpg)\n")
        renderer.finalize()
        
        result = output.getvalue()
        # Image placeholder should contain the URL
        assert "example.com" in result

    def test_image_in_paragraph(self):
        """Test image within paragraph"""
        output = StringIO()
        renderer = MarkdownRenderer(output=output)
        
        renderer.render("Here is an image: ![test](http://test.com/a.png) in text\n")
        renderer.finalize()
        
        result = output.getvalue()
        assert "test" in result
        assert "test.com" in result


class TestFootnotes:
    """Test footnote support"""

    def test_footnote_basic(self):
        """Test basic footnote"""
        output = StringIO()
        renderer = MarkdownRenderer(output=output)
        
        renderer.render("This has a footnote[^1].\n")
        renderer.render("\n")
        renderer.render("[^1]: This is the footnote.\n")
        renderer.finalize()
        
        result = output.getvalue()
        assert "[1]" in result
        assert "Footnotes:" in result
        assert "This is the footnote" in result

    def test_footnote_multiple(self):
        """Test multiple footnotes"""
        output = StringIO()
        renderer = MarkdownRenderer(output=output)
        
        renderer.render("First[^1] and second[^2] footnotes.\n")
        renderer.render("\n")
        renderer.render("[^1]: First footnote text.\n")
        renderer.render("[^2]: Second footnote text.\n")
        renderer.finalize()
        
        result = output.getvalue()
        assert "First footnote text" in result
        assert "Second footnote text" in result

    def test_footnote_named(self):
        """Test named footnote"""
        output = StringIO()
        renderer = MarkdownRenderer(output=output)
        
        renderer.render("Reference[^note].\n")
        renderer.render("\n")
        renderer.render("[^note]: Named footnote content.\n")
        renderer.finalize()
        
        result = output.getvalue()
        assert "Named footnote content" in result


class TestDefinitionLists:
    """Test definition list support"""

    def test_definition_basic(self):
        """Test basic definition list"""
        output = StringIO()
        renderer = MarkdownRenderer(output=output)
        
        renderer.render("Term : Definition text\n")
        renderer.finalize()
        
        result = output.getvalue()
        assert "Term" in result
        assert "Definition text" in result
        assert ":" in result

    def test_definition_multiple(self):
        """Test multiple definitions"""
        output = StringIO()
        renderer = MarkdownRenderer(output=output)
        
        renderer.render("Apple : A fruit\n")
        renderer.render("Carrot : A vegetable\n")
        renderer.finalize()
        
        result = output.getvalue()
        assert "Apple" in result
        assert "fruit" in result
        assert "Carrot" in result
        assert "vegetable" in result

    def test_definition_with_formatting(self):
        """Test definition with inline formatting"""
        output = StringIO()
        renderer = MarkdownRenderer(output=output)
        
        renderer.render("**Bold Term** : *Italic definition*\n")
        renderer.finalize()
        
        result = output.getvalue()
        assert "Bold Term" in result
        assert "Italic definition" in result


class TestCustomThemes:
    """Test custom theme registration"""

    def test_register_custom_theme(self):
        """Test registering a custom theme"""
        custom_theme = {
            'name': 'custom-test',
            'pygments_style': 'monokai',
            'heading_colors': {
                1: '#ff0000',
                2: '#00ff00',
                3: '#0000ff',
                4: '#ffff00',
                5: '#00ffff',
                6: '#ff00ff',
            },
            'inline_code': '#123456',
            'link': '#654321',
            'blockquote_border': '#aaaaaa',
            'table_border': '#bbbbbb',
            'checkbox_unchecked': '#cccccc',
            'checkbox_checked': '#ddddd',
            'hr': '#eeeeee',
            'highlight': '#ffffff',
            'list_marker': '#111111',
            'table_header': '#222222',
        }
        
        register_theme('custom-test', custom_theme)
        
        # Verify theme is registered
        from markrender.themes import get_theme
        theme = get_theme('custom-test')
        assert theme is not None
        assert theme['name'] == 'custom-test'

    def test_use_custom_theme(self):
        """Test using a custom theme"""
        custom_theme = {
            'name': 'render-test',
            'pygments_style': 'monokai',
            'heading_colors': {1: '#ff0000'},
            'inline_code': '#00ff00',
            'link': '#0000ff',
            'blockquote_border': '#aaaaaa',
            'table_border': '#bbbbbb',
            'checkbox_unchecked': '#cccccc',
            'checkbox_checked': '#dddddd',
            'hr': '#eeeeee',
            'highlight': '#ffffff',
            'list_marker': '#111111',
            'table_header': '#222222',
        }
        
        register_theme('render-test', custom_theme)
        
        output = StringIO()
        renderer = MarkdownRenderer(theme='render-test', output=output)
        
        renderer.render("# Test\n")
        renderer.finalize()
        
        result = output.getvalue()
        assert "Test" in result


class TestConfigLoading:
    """Test configuration loading"""

    def test_config_default_values(self):
        """Test default configuration values"""
        from markrender.config import get_config
        
        config = get_config()
        assert 'theme' in config
        assert 'line_numbers' in config
        assert 'code_background' in config

    def test_renderer_uses_config(self):
        """Test that renderer can use config"""
        # This test verifies the config integration works
        output = StringIO()
        renderer = MarkdownRenderer(output=output, use_config=False)
        
        renderer.render("# Test\n")
        renderer.finalize()
        
        result = output.getvalue()
        assert "Test" in result
