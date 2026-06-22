"""
Footnotes Example
Demonstrates footnote syntax and rendering
"""

from markrender import MarkdownRenderer


def main():
    """Demonstrate footnote rendering"""
    
    renderer = MarkdownRenderer(
        theme='github-dark',
        line_numbers=False
    )
    
    markdown_content = """
# Footnotes Examples

Add scholarly footnotes to your documents.

## Basic Footnotes

This is a statement with a footnote reference.[^1]

Here is another claim that needs citation.[^research]

You can have multiple footnotes in the same document.[^3]

## Footnote Definitions

[^1]: This is the first footnote. It provides additional information about the statement above. Footnotes can be multiple sentences long.

[^research]: According to research conducted in 2024, this claim has been verified by multiple studies.

[^3]: A shorter footnote example.

## Named Footnotes

Python is a popular programming language.[^python-fact]

It was created by Guido van Rossum.[^creator]

[^python-fact]: Python consistently ranks as one of the most popular programming languages according to the TIOBE Index and Stack Overflow surveys.

[^creator]: Guido van Rossum began working on Python in the late 1980s as a successor to the ABC programming language.

## In Technical Writing

The algorithm has O(n log n) complexity.[^complexity]

This approach was first described by Smith et al.[^smith2020]

[^complexity]: The time complexity is O(n log n) in the average case, and O(n²) in the worst case when the pivot selection is poor.

[^smith2020]: Smith, J., Johnson, A., & Williams, B. (2020). "Efficient Algorithms for Data Processing". Journal of Computer Science, 45(3), 123-145.

## Tips

- Keep footnotes concise
- Use meaningful identifiers
- Place definitions at the end
- Footnotes are automatically numbered

Footnotes are collected and displayed at the end of the document!
"""
    
    print("=" * 70)
    print("Footnotes Demo")
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
