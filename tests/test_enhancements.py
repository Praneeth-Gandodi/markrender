import pytest
from markrender import MarkdownRenderer
import io
import re

def strip_ansi(text):
    return re.sub(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])', '', text)

@pytest.fixture
def renderer_output():
    output = io.StringIO()
    renderer = MarkdownRenderer(output=output, force_color=True, width=80)
    return renderer, output

def test_callout_rendering(renderer_output):
    renderer, output = renderer_output
    renderer.render("> [!NOTE] This is a note\n")
    renderer.render("> With multiple lines\n")
    renderer.render("\n")
    renderer.finalize()
    
    val = output.getvalue()
    # Check for Note icon/text
    assert "NOTE" in val
    # Check for color (blue-ish for note usually, but just check content for now)
    assert "This is a note" in val
    assert "With multiple lines" in val

def test_nested_blockquotes(renderer_output):
    renderer, output = renderer_output
    renderer.render("> Level 1\n")
    renderer.render(">> Level 2\n")
    renderer.render(">>> Level 3\n")
    renderer.render("\n")
    renderer.finalize()
    
    val = strip_ansi(output.getvalue())
    assert "│ Level 1" in val
    # Level 2 should have 2 borders or indentation
    assert "│ │ Level 2" in val
    assert "│ │ │ Level 3" in val

def test_nested_lists(renderer_output):
    renderer, output = renderer_output
    renderer.render("- Item 1\n  - Item 1.1\n    - Item 1.1.1\n")
    renderer.finalize()

    val = strip_ansi(output.getvalue())
    assert "● Item 1" in val
    assert "  ○ Item 1.1" in val
    assert "    ■ Item 1.1.1" in val

def test_robust_table_flushing(renderer_output):
    renderer, output = renderer_output
    # Table with varying columns and extra spaces
    renderer.render("| Col 1 | Col 2 |\n")
    renderer.render("|---|---|\n")
    renderer.render("| Val 1 |\n") # Missing 2nd col
    renderer.render("| Val A | Val B | Val C |\n") # Extra col
    renderer.finalize()
    
    val = strip_ansi(output.getvalue())
    assert "Col 1" in val
    assert "Col 2" in val
    assert "Val 1" in val
    assert "Val B" in val
    # Val C might be truncated or rendered, depending on implementation.
    # Current implementation truncates to header length.
    assert "Val C" not in val 

def test_streaming_inline_split(renderer_output):
    renderer, output = renderer_output
    # Split bold across chunks
    renderer.render("This is **bo")
    renderer.render("ld** text.\n")
    renderer.finalize()
    
    val = strip_ansi(output.getvalue())
    assert "This is bold text." in val
    
    # Verify ANSI codes are present (meaning it was formatted)
    raw_val = output.getvalue()
    assert "\x1b[1m" in raw_val # Bold start

def test_interrupted_table(renderer_output):
    renderer, output = renderer_output
    renderer.render("| A | B |\n")
    renderer.render("|---|---|\n")
    renderer.render("| 1 | 2 |\n")
    renderer.render("Interruption\n")
    renderer.render("| 3 | 4 |\n")
    renderer.finalize()
    
    val = strip_ansi(output.getvalue())
    assert "A" in val
    assert "1" in val
    assert "Interruption" in val
    # "3" and "4" might be treated as text or new table depending on separator requirement
    # Since second table has no separator, it should probably be treated as text or malformed
    assert "3" in val
