
import sys
import os
from io import StringIO

# Add parent directory to path to import markrender
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from markrender.renderer import MarkdownRenderer

def test_full_rendering():
    print("Testing Full Rendering...")
    
    # Capture output
    output = StringIO()
    renderer = MarkdownRenderer(theme='github-dark', output=output, force_color=True)
    
    markdown_content = """
# Heading 1

This is a paragraph with **bold** and *italic* and `inline code`.

- List item 1
- List item 2 with **bold**

| Header 1 | Header 2 |
| -------- | -------- |
| Cell 1   | Cell 2   |
| **Bold** | `Code`   |

> Blockquote with **bold**

[Link](https://example.com) with **bold** inside.
"""
    
    # Simulate streaming
    chunk_size = 10
    for i in range(0, len(markdown_content), chunk_size):
        renderer.render(markdown_content[i:i+chunk_size])
        
    renderer.finalize()
    
    result = output.getvalue()
    print("Rendered Output Length:", len(result))
    
    # We can't easily assert on ANSI codes without a complex parser, 
    # but we can check if it ran without error and produced output.
    # And we can heuristically check for ANSI codes.
    
    if len(result) > len(markdown_content):
        print("PASS: Output contains ANSI codes (length increased)")
    else:
        print("FAIL: Output length suspiciously short (no color codes?)")
        
    # Check for specific colors
    # github-dark H1 color: 38;2;88;166;255
    if "38;2;88;166;255" in result:
        print("PASS: Heading color ANSI code found")
    else:
        print("FAIL: Heading color ANSI code NOT found")
        
    # Check for inline code color: 38;2;201;158;255
    if "38;2;201;158;255" in result:
        print("PASS: Inline code color ANSI code found")
    else:
        print("FAIL: Inline code color ANSI code NOT found")

if __name__ == "__main__":
    test_full_rendering()
