"""
Basic usage example for MarkRender
Demonstrates rendering static markdown content
"""

from markrender import MarkdownRenderer


def main():
    """Basic markdown rendering example"""
    
    # Create renderer with default theme
    renderer = MarkdownRenderer(theme='github-dark')
    
    # Sample markdown content
    markdown = """
# MarkRender Demo

Welcome to **MarkRender** - a professional terminal markdown renderer!

## Features

Here are some key features:

- 🎨 Beautiful syntax highlighting
- 📊 Table rendering
- ✅ Task lists
- 😊 Emoji support
- And much more!

## Code Example

```python
from markrender import MarkdownRenderer

renderer = MarkdownRenderer()
renderer.render("# Hello World")
renderer.finalize()
```

## Task List

- [x] Install MarkRender
- [x] Read documentation
- [ ] Build something awesome!

## Table Example

| Feature | Status |
|---------|--------|
| Headings | ✓ |
| Code Blocks | ✓ |
| Tables | ✓ |

## Links and Formatting

Visit [GitHub](https://github.com) for more info.

Use `inline code` for short snippets.

> This is a blockquote.
> It can span multiple lines!

---

Made with ❤️ using MarkRender
"""
    
    # Render the markdown
    print("Rendering markdown content...\n")
    renderer.render(markdown)
    renderer.finalize()


if __name__ == '__main__':
    main()
