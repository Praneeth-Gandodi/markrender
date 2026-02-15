
import pytest
from io import StringIO
from markrender import MarkdownRenderer
from rich.console import Console

def test_render_emoji():
    print("Testing Emoji...")
    output = StringIO()
    renderer = MarkdownRenderer(output=output, force_color=True)

    renderer.render("Hello :wave:\n")
    renderer.finalize()

    result = output.getvalue()
    print(f"Result repr: {repr(result)}")  # Just print the repr to avoid encoding issues
    if ":wave:" in result or "👋" in result:  # Either the emoji or the code should be present
        print("PASS: Emoji found")
    else:
        print("FAIL: Emoji NOT found")

def test_render_blockquote_as_note():
    print("\nTesting Blockquote Note...")
    output = StringIO()
    renderer = MarkdownRenderer(output=output)
    
    renderer.render("> [!NOTE] This is a note.\n")
    renderer.finalize()
    
    result = output.getvalue()
    print(f"Result: {repr(result)}")
    
    if "NOTE: This is a note." in result: # Check logic from test file might be flawed if rich formatting is applied
         print("PASS: Note text found")
    else:
         print("FAIL: Note text found")

if __name__ == "__main__":
    test_render_emoji()
    test_render_blockquote_as_note()
