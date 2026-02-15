"""
Tests for edge cases in the MarkdownRenderer
"""

import io
import re
import pytest
from markrender import MarkdownRenderer

def strip_ansi(text):
    return re.sub(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])', '', text)

@pytest.fixture
def renderer_output():
    output = io.StringIO()
    renderer = MarkdownRenderer(output=output, force_color=True)
    return renderer, output

def test_incomplete_bold_at_end_of_chunk(renderer_output):
    renderer, output = renderer_output
    renderer.render("This is **bold")
    renderer.render(" and this is not**.")
    renderer.finalize()
    
    output_val = output.getvalue()
    # This is still tricky, but we can check for the bold ANSI codes
    assert "\x1b[1m" in output_val
    assert "\x1b[0m" in output_val

def test_table_split_across_chunks(renderer_output):
    renderer, output = renderer_output
    renderer.render("| Header 1 |")
    renderer.render(" Header 2 |\n")
    renderer.render("|---|---|\n")
    renderer.render("| Cell 1 |")
    renderer.render(" Cell 2 |")
    renderer.finalize()

    output_val = output.getvalue()
    assert "Header 1" in output_val
    assert "Header 2" in output_val
    assert "Cell 1" in output_val
    assert "Cell 2" in output_val

def test_nested_blockquotes(renderer_output):
    renderer, output = renderer_output
    renderer.render("> Outer\n")
    renderer.render("> > Inner\n")
    renderer.render("> Outer again\n")
    renderer.finalize()

    output_val = output.getvalue()
    clean_output = strip_ansi(output_val)
    # This will likely fail, as nested blockquotes are not supported.
    assert "│ Outer" in clean_output
    assert "│ Inner" in clean_output
    assert "│ Outer again" in clean_output

def test_stray_backticks_in_code_block(renderer_output):
    renderer, output = renderer_output
    renderer.render("```python\n")
    renderer.render("print('```')\n")
    renderer.render("```\n")
    renderer.finalize()

    output_val = output.getvalue()
    assert "print" in output_val
    assert "```" in output_val


def test_table_with_fewer_columns_in_a_row(renderer_output):
    renderer, output = renderer_output
    renderer.render("| Header 1 | Header 2 |\n")
    renderer.render("|---|---|\n")
    renderer.render("| Cell 1 |\n")
    renderer.finalize()

    output_val = output.getvalue()
    clean_output = strip_ansi(output_val)
    assert "Header 1" in clean_output
    assert "Header 2" in clean_output
    assert "Cell 1" in clean_output

def test_table_with_more_columns_in_a_row(renderer_output):
    renderer, output = renderer_output
    renderer.render("| Header 1 | Header 2 |\n")
    renderer.render("|---|---|\n")
    renderer.render("| Cell 1 | Cell 2 | Cell 3 |\n")
    renderer.finalize()

    output_val = output.getvalue()
    clean_output = strip_ansi(output_val)
    assert "Header 1" in clean_output
    assert "Header 2" in clean_output
    assert "Cell 1" in clean_output
    assert "Cell 2" in clean_output
    assert "Cell 3" not in clean_output

def test_table_interrupted_by_non_table_line(renderer_output):
    renderer, output = renderer_output
    renderer.render("| Header 1 | Header 2 |\n")
    renderer.render("|---|---|\n")
    renderer.render("| Cell 1 | Cell 2 |\n")
    renderer.render("This is not a table line\n")
    renderer.render("| Cell 3 | Cell 4 |\n")
    renderer.finalize()

    output_val = output.getvalue()
    clean_output = strip_ansi(output_val)
    assert "Header 1" in clean_output
    assert "This is not a table line" in clean_output
    assert "Cell 3" in clean_output

def test_table_with_empty_cell(renderer_output):
    renderer, output = renderer_output
    renderer.render("| Header 1 | Header 2 |\n")
    renderer.render("|---|---|\n")
    renderer.render("| Cell 1 | |\n")
    renderer.finalize()

    output_val = output.getvalue()
    clean_output = strip_ansi(output_val)
    assert "Header 1" in clean_output
    assert "Cell 1" in clean_output

def test_table_with_inline_formatting(renderer_output):
    renderer, output = renderer_output
    renderer.render("| *Header* 1 | **Header** 2 |\n")
    renderer.render("|---|---|\n")
    renderer.render("| `Cell` 1 | [Link](http://example.com) |\n")
    renderer.finalize()

    output_val = output.getvalue()
    # Don't strip ansi here, as we are checking for formatting
    assert "Header" in output_val
    assert "Cell" in output_val
    assert "Link" in output_val
