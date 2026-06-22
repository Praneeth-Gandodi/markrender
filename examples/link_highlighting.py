"""
Link Highlighting Example
Demonstrates enhanced link rendering with icons
"""

from markrender import MarkdownRenderer


def main():
    """Demonstrate enhanced link highlighting"""
    
    renderer = MarkdownRenderer(
        theme='github-dark',
        line_numbers=False
    )
    
    markdown_content = """
# Enhanced Link Highlighting

Links are now rendered with icons based on their type!

## Web Links

Secure HTTPS links: [GitHub](https://github.com)

Regular HTTP links: [Example](http://example.com)

## Email and Phone

Email links: [Contact Us](mailto:hello@example.com)

Phone links: [Call Now](tel:+1234567890)

## Multiple Links

Here are multiple links in one line:

[GitHub](https://github.com) | [Google](https://google.com) | [Email](mailto:test@example.com)

## In Context

Check out these resources:

- Official docs: [Python Docs](https://docs.python.org)
- Source code: [MarkRender on GitHub](https://github.com/Praneeth-Gandodi/markrender)
- Support: [Contact Support](mailto:support@example.com)
- Demo site: [Live Demo](http://demo.example.com)

Links make navigation easy!
"""
    
    print("=" * 70)
    print("Enhanced Link Highlighting Demo")
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
