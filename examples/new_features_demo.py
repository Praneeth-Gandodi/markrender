"""
MarkRender New Features Demo
Demonstrates all the new features added in version 2.0.0
"""

from markrender import MarkdownRenderer


def demo_all_features():
    """Demonstrate all new MarkRender features"""
    
    renderer = MarkdownRenderer(
        theme='github-dark',
        line_numbers=True,
        code_background=False
    )
    
    markdown_content = """
# MarkRender 2.0.0 Features Demo

## 1. Highlighted Text

Use ==highlight== syntax to emphasize important text.

This is ==highlighted text== for emphasis.

You can combine with other formatting:
- ==**bold highlight**==
- ==*italic highlight*==
- ==`code highlight`==

## 2. Nested Lists

### Unordered Nested Lists

- Main item 1
  - Sub-item 1.1
    - Deep nested item 1.1.1
    - Deep nested item 1.1.2
  - Sub-item 1.2
- Main item 2
  - Sub-item 2.1
  - Sub-item 2.2

### Ordered Nested Lists

1. First item
   1. Sub-item 1.1
   2. Sub-item 1.2
      1. Deep item 1.2.1
2. Second item
   1. Sub-item 2.1
3. Third item

### Mixed Nested Lists

1. Ordered parent
   - Unordered child
   - Another unordered child
2. Another ordered parent
   - More unordered children

## 3. Progress Bars

Track task progress with visual progress bars:

- [0%] Not started
- [10%] Just started
- [25%] In progress (early)
- [50%] Halfway complete
- [75%] Almost done
- [90%] Nearly finished
- [100%] Completed

Progress bars are color-coded:
- Red: 0-24%
- Orange: 25-49%
- Yellow: 50-74%
- Green: 75-99%
- Checkmark: 100%

## 4. Image Placeholders

Since terminals cannot display actual images, MarkRender renders beautiful placeholders:

![System Architecture Diagram](https://example.com/architecture.png)

Another example: ![Logo](https://example.com/logo.jpg)

## 5. Footnotes

Add scholarly footnotes to your documents:

This is an important statement that requires additional context.[^1]

Here is another claim that needs citation.[^research]

You can have multiple footnotes in the same document.[^3]

[^1]: This is the first footnote. It provides additional information about the statement above. Footnotes can be multiple sentences long.

[^research]: According to research conducted in 2024, this claim has been verified.

[^3]: A shorter footnote example.

## 6. Definition Lists

Create glossaries and definition lists:

**Python** : A high-level programming language known for its simplicity and readability.

**API** : Application Programming Interface - allows different software components to communicate.

**Markdown** : A lightweight markup language for creating formatted text using plain text.

**MarkRender** : A Python library for rendering Markdown in the terminal with beautiful formatting.

**Rich** : A Python library for rich text and beautiful formatting in the terminal.

## 7. Combined Example

Here is how all features work together:

### Task Progress with Notes

- [25%] ==Planning phase== complete[^planning]
- [50%] Design in progress
  - Architecture documented
  - UI mockups created
- [75%] Implementation
  - Core features done
  - Testing underway

[^planning]: The planning phase included requirements gathering and stakeholder meetings.

### Code with Highlights

```python
def process_data(items):
    # Process a list of items
    results = []
    for item in items:
        if item.is_valid():  # ==Important check==
            results.append(item.transform())
    return results
```

### Image Reference

See the flowchart below:

![Data Processing Flow](https://example.com/flowchart.png)

---

## Summary

MarkRender 2.0.0 includes:

1. ==Highlight syntax== for emphasis
2. ==Nested lists== with proper indentation
3. ==Progress bars== for task tracking
4. ==Image placeholders== for visual references
5. ==Footnotes== for citations and notes
6. ==Definition lists== for glossaries
7. CLI interface for command-line usage
8. Configuration file support
9. Custom theme registration

For more information, visit the [GitHub repository](https://github.com/Praneeth-Gandodi/markrender).
"""
    
    print("=" * 80)
    print("MarkRender 2.0.0 - New Features Demonstration")
    print("=" * 80)
    print()
    
    renderer.render(markdown_content)
    renderer.finalize()
    
    print()
    print("=" * 80)
    print("Demo complete!")
    print("=" * 80)


if __name__ == '__main__':
    demo_all_features()
