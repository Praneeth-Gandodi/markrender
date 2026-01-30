"""
Theme showcase for MarkRender
Displays all available themes with sample code
"""

from markrender import MarkdownRenderer
from markrender.themes import list_themes


def main():
    """Showcase all available themes"""
    
    # Sample code for demonstration
    sample_code = """
```python
def fibonacci(n):
    \"\"\"Calculate Fibonacci number\"\"\"
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

# Test the function
result = fibonacci(10)
print(f"Fibonacci(10) = {result}")
```
"""
    
    print("=" * 80)
    print("MarkRender Theme Showcase")
    print("=" * 80)
    print()
    
    # Display each theme
    for theme_name in list_themes():
        print(f"\n{'─' * 80}")
        print(f"Theme: {theme_name.upper()}")
        print('─' * 80)
        
        # Create renderer with this theme
        renderer = MarkdownRenderer(
            theme=theme_name,
            line_numbers=True,
            code_background=False
        )
        
        # Render sample
        renderer.render(f"## {theme_name.title()} Theme\n\n")
        renderer.render("Here's some `inline code` and **bold text**.\n\n")
        renderer.render(sample_code)
        renderer.finalize()
        
        print()
    
    print("\n" + "=" * 80)
    print("End of theme showcase")
    print("=" * 80)


if __name__ == '__main__':
    main()
