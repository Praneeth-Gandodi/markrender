import sys
import os
from io import StringIO

# Add parent directory to path to import markrender
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from markrender.renderer import MarkdownRenderer

# Capture output
output = StringIO()
renderer = MarkdownRenderer(theme='github-dark', output=output, force_color=True)

markdown_content = """
# Heading 1

This is a paragraph with `inline code`.
"""

# Render the content
renderer.render(markdown_content)
renderer.finalize()

result = output.getvalue()
print("Full output:")
print(repr(result))
print("\nActual output:")
print(result)
print("\nLooking for ANSI codes:")
print("Contains '38;2;88;166;255' (H1 color):", "38;2;88;166;255" in result)
print("Contains '38;2;201;158;255' (inline code color):", "38;2;201;158;255" in result)