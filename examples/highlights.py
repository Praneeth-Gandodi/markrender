"""
Highlights Feature Example
Demonstrates ==highlighted text== syntax
"""

from markrender import MarkdownRenderer


def main():
    """Demonstrate highlight syntax"""
    
    renderer = MarkdownRenderer(
        theme='github-dark',
        line_numbers=False
    )
    
    markdown_content = """
# Highlighted Text Examples

Use ==text== syntax to highlight important information.

## Basic Highlights

This is ==highlighted text== for emphasis.

Normal text with ==a highlight== in the middle.

## Combined Formatting

==**Bold highlight**== for important items.

==*Italic highlight*== for subtle emphasis.

==`Code highlight`== for code references.

## Use Cases

### Key Points

- ==Important==: Remember to save your work
- ==Warning==: This action cannot be undone
- ==Note==: Configuration required

### Documentation

The ==config.toml== file must be in the root directory.

Use the ==--help== flag to see available options.

### Code Comments

This function ==must not be modified== without approval.

The ==v2.0.0== release includes breaking changes.

## Multiple Highlights

This sentence has ==multiple== ==highlights== for demonstration.

You can also have a ==very long highlighted section that spans multiple words and phrases== in a single highlight.

---

Highlights are great for:
- Emphasizing key information
- Drawing attention to important notes
- Marking action items
- Highlighting code references
"""
    
    print("=" * 70)
    print("Highlighted Text Demo")
    print("=" * 70)
    print()
    
    renderer.render(markdown_content)
    renderer.finalize()
    
    print()
    print("=" * 70)
    print("Demo complete!")
    print("=" * 70)


if __name__ == '__main__':
    main()
