"""
Complete Features Showcase
Demonstrates all MarkRender features in one document
"""

from markrender import MarkdownRenderer


def main():
    """Comprehensive feature demonstration"""
    
    renderer = MarkdownRenderer(
        theme='github-dark',
        line_numbers=True,
        code_background=False
    )
    
    markdown_content = """
# MarkRender Complete Feature Showcase

This document demonstrates all features of MarkRender v1.0.5.

## 1. Text Formatting

Basic formatting: **bold**, *italic*, `inline code`, and ==highlighted==.

Strikethrough: ~~deleted text~~

## 2. Enhanced Links

- [GitHub Repository](https://github.com)
- [Documentation](https://docs.python.org)
- [Contact](mailto:hello@example.com)

## 3. Nested Lists

### Unordered
- Item 1
  - Nested 1.1
    - Deep item
  - Nested 1.2
- Item 2

### Ordered
1. First
   1. Sub-first
   2. Sub-second
2. Second

### Mixed
1. Ordered
   - Unordered nested
   - Another item
2. Back to ordered

## 4. Progress Bars

Project Status:

- [100%] Planning phase
- [75%] Development
- [50%] Testing
- [25%] Documentation
- [0%] Deployment

## 5. Code Blocks

```python
def greet(name):
    return f"Hello, {name}!"

print(greet("World"))
```

## 6. Mermaid Diagrams

```mermaid
graph TD
    A[Start] --> B{Condition}
    B -->|Yes| C[Action 1]
    B -->|No| D[Action 2]
    C --> E[End]
    D --> E
```

## 7. Tables

| Feature | Status | Priority |
|---------|--------|----------|
| Core | ✅ Done | High |
| Advanced | ✅ Done | Medium |
| Extras | 🔄 In Progress | Low |

## 8. Blockquotes

> This is a standard blockquote.
> It can span multiple lines.

### Callout Style

> [!NOTE]
> This is a note callout for important information.

> [!TIP]
> Here's a helpful tip for users.

> [!WARNING]
> Be careful with this operation!

## 9. Footnotes

MarkRender supports footnotes.[^1]

They appear at the end.[^2]

[^1]: This is the first footnote with detailed explanation.
[^2]: A second footnote for demonstration.

## 10. Definition Lists

**MarkRender** : A terminal markdown renderer for Python.

**Rich** : The library powering the beautiful output.

**Pygments** : Provides syntax highlighting.

## 11. Images

![Architecture Diagram](https://example.com/diagram.png)

## 12. Checkboxes

Task list:

- [x] Completed task
- [ ] Pending task
- [x] Another completed task

---

## Summary

MarkRender provides comprehensive markdown rendering for terminals:

1. ✅ Text formatting
2. ✅ Enhanced links with icons
3. ✅ Nested lists
4. ✅ Progress bars
5. ✅ Syntax highlighting
6. ✅ Mermaid diagrams
7. ✅ Tables
8. ✅ Blockquotes & callouts
9. ✅ Footnotes
10. ✅ Definition lists
11. ✅ Image placeholders
12. ✅ Checkboxes

Perfect for documentation, README files, and LLM responses!
"""
    
    print("=" * 70)
    print("MarkRender v1.0.5 - Complete Feature Showcase")
    print("=" * 70)
    print()
    
    renderer.render(markdown_content)
    renderer.finalize()
    
    print()
    print("=" * 70)
    print("All features demonstrated!")
    print("=" * 70)


if __name__ == '__main__':
    main()
