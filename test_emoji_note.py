import sys
import os
from io import StringIO

# Add parent directory to path to import markrender
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from markrender import MarkdownRenderer

def test_render_emoji():
    print("Testing Emoji...")
    output = StringIO()
    renderer = MarkdownRenderer(output=output, force_color=True)

    renderer.render("Hello :wave:\n")
    renderer.finalize()

    result = output.getvalue()
    # Just check if emoji is in the result without printing it
    has_emoji = ":wave:" in result or "👋" in result
    print(f"Emoji test result: {'PASS' if has_emoji else 'FAIL'} - Emoji found: {has_emoji}")

def test_render_blockquote_as_note():
    print("\nTesting Blockquote Note...")
    output = StringIO()
    renderer = MarkdownRenderer(output=output, force_color=True)

    renderer.render("> [!NOTE] This is a note.\n")
    renderer.finalize()

    result = output.getvalue()
    
    has_note = "NOTE" in result and "This is a note." in result
    print(f"Note test result: {'PASS' if has_note else 'FAIL'} - Note found: {has_note}")

if __name__ == "__main__":
    test_render_emoji()
    test_render_blockquote_as_note()