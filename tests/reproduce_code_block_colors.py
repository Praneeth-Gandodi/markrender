
import sys
import os
from rich.console import Console
from rich.text import Text

# Add parent directory to path to import markrender
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from markrender.formatters import MarkdownFormatter
from markrender.themes import get_theme

def test_code_block_colors():
    print("Testing Code Block Colors...")
    theme = get_theme('github-dark')
    formatter = MarkdownFormatter(theme)
    
    code = "def hello():\n    print('world')"
    language = "python"
    
    print(f"\n--- Testing format_code_block ({language}) ---")
    formatted = formatter.format_code_block(code, language)
    
    if isinstance(formatted, Text):
        print("PASS: Returned Text object")
        # Check if there are any styles applied to the text
        # We expect some spans to have colors
        
        found_color = False
        print("Spans found:")
        for span in formatted.spans:
            print(f"  - {span}")
            if span.style:
                found_color = True
        
        if found_color:
            print("PASS: Styles found in code block")
        else:
            print("FAIL: No styles found in code block")
            
        console = Console()
        console.print(formatted)
    else:
        print(f"FAIL: Returned {type(formatted)}, expected Text")

def test_stream_code_line():
    print("\n--- Testing stream_code_line ---")
    theme = get_theme('github-dark')
    formatter = MarkdownFormatter(theme)
    
    line = "def hello():"
    language = "python"
    
    formatted_line = formatter.stream_code_line(line, language)
    
    if isinstance(formatted_line, Text):
         found_color = False
         for span in formatted_line.spans:
             print(f"  - {span}")
             if span.style:
                 found_color = True
         
         if found_color:
             print("PASS: Styles found in stream_line")
         else:
             print("FAIL: No styles found in stream_line")
         
         console = Console()
         console.print(formatted_line)

if __name__ == "__main__":
    test_code_block_colors()
    test_stream_code_line()
