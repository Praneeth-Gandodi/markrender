"""
Definition Lists Example
Demonstrates Term : Definition syntax
"""

from markrender import MarkdownRenderer


def main():
    """Demonstrate definition list rendering"""
    
    renderer = MarkdownRenderer(
        theme='github-dark',
        line_numbers=False
    )
    
    markdown_content = """
# Definition Lists Examples

Use `Term : Definition` syntax for glossaries and definitions.

Note: Use two or more spaces around the colon for proper recognition.

## Programming Terms

**Python** : A high-level programming language known for its simplicity and readability.

**API** : Application Programming Interface - allows different software components to communicate.

**Framework** : A pre-built structure that provides generic functionality which can be changed by the user.

**Library** : A collection of pre-written code that developers can use to perform common tasks.

## Web Development

**HTML** : HyperText Markup Language - the standard markup language for documents designed to be displayed in a web browser.

**CSS** : Cascading Style Sheets - a style sheet language used for describing the presentation of a document written in HTML.

**JavaScript** : A programming language that powers the dynamic behavior of web pages.

**React** : A JavaScript library for building user interfaces, developed by Facebook.

## Data Science

**Machine Learning** : A subset of artificial intelligence that enables systems to learn and improve from experience without being explicitly programmed.

**Neural Network** : A computing system inspired by biological neural networks that constitute animal brains.

**Dataset** : A collection of related sets of information that is composed of separate elements but can be manipulated as a unit by a computer.

## Mixed Content

You can use **bold**, *italic*, and `code` in definitions.

**Important Note** : This is ==highlighted== for emphasis.

---

Definition lists are perfect for:
- Glossaries
- Documentation
- API references
- Terminology guides
"""
    
    print("=" * 70)
    print("Definition Lists Demo")
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
