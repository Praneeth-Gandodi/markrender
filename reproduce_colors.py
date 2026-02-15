
import sys
import os
from rich.console import Console
from rich.text import Text

# Add parent directory to path to import markrender
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from markrender.formatters import MarkdownFormatter
from markrender.themes import get_theme
from markrender.colors import get_rich_color_style, Colors
from markrender.parser import MarkdownParser

def test_heading_color():
    print("Testing Heading Color...")
    theme = get_theme('github-dark')
    formatter = MarkdownFormatter(theme)
    
    # Test H1
    h1 = formatter.format_heading(1, "Test Heading")
    print(f"Type: {type(h1)}")
    
    if isinstance(h1, Text):
        found_blue = False
        for span in h1.spans:
            print(f"Span: {span}")
            # github-dark H1 is rgb(88,166,255)
            if "rgb(88,166,255)" in str(span.style):
                found_blue = True
            
        if found_blue:
            print("PASS: Heading color found")
        else:
            print("FAIL: Heading color NOT found")
    else:
        print("FAIL: Heading is not a Text object")

def test_inline_code():
    print("\nTesting Inline Code...")
    theme = get_theme('github-dark')
    formatter = MarkdownFormatter(theme)
    
    code_text = "print('hello')"
    formatted = formatter.format_inline_code(code_text)
    print(f"Output type: {type(formatted)}")
    
    if isinstance(formatted, Text):
        print("PASS: format_inline_code returns Text object")
        print(f"Style: {formatted.style}")
    else:
        print("FAIL: format_inline_code returns str")

def test_apply_inline_formatting():
    print("\nTesting apply_inline_formatting...")
    parser = MarkdownParser()
    theme = get_theme('github-dark')
    formatter = MarkdownFormatter(theme)
    
    text = "Some `code` and **bold** and [link](url)"
    formatted = parser.apply_inline_formatting(text, formatter)
    print(f"Output type: {type(formatted)}")
    
    if isinstance(formatted, Text):
        print("PASS: returns Text object")
        print(f"Spans: {formatted.spans}")
        
        code_found = False
        bold_found = False
        link_found = False
        
        # We need to check spans or style of segments?
        # apply_inline_formatting concatenates text objects.
        # Spans should be preserved.
        
        for span in formatted.spans:
            s = str(span.style)
            # print(f"Checking span: {s}")
            # Inline code usually has color.
            if "rgb" in s and "bold" not in s and "underline" not in s: 
                code_found = True
            if "bold" in s:
                bold_found = True
            if "link=" in s or "underline" in s: # Link style usually has underline
                link_found = True
        
        if code_found: print("PASS: Code style found")
        else: print("FAIL: Code style not found")
        
        if bold_found: print("PASS: Bold style found")
        else: print("FAIL: Bold style not found")
        
        if link_found: print("PASS: Link style found")
        else: print("FAIL: Link style not found")

    else:
        print("FAIL: returns str")

def test_nested_formatting():
    print("\nTesting Nested Formatting (**bold** inside link)...")
    parser = MarkdownParser()
    theme = get_theme('github-dark')
    formatter = MarkdownFormatter(theme)
    
    text = "[**Bold Link**](https://example.com)"
    formatted = parser.apply_inline_formatting(text, formatter)
    
    if isinstance(formatted, Text):
        print(f"Spans: {formatted.spans}")
        # Look for a span that is bold AND has a link? 
        # Or two spans covering the same range.
        
        has_bold = False
        has_link = False
        
        for span in formatted.spans:
            s = str(span.style)
            if "bold" in s: has_bold = True
            if "link=" in s: has_link = True
            
        if has_bold and has_link:
            print("PASS: Nested formatting preserved")
        else:
            print(f"FAIL: Missing styles. Bold: {has_bold}, Link: {has_link}")

if __name__ == "__main__":
    test_heading_color()
    test_inline_code()
    test_apply_inline_formatting()
    test_nested_formatting()
