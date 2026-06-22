"""
Showcase of new features in markrender v1.0.7
- Dim mode (Thinking mode)
- OSC 8 Clickable Hyperlinks
- File Tree rendering
- Improved List support
- Robust Word Wrapping
"""

from markrender import MarkdownRenderer

def demonstrate_v1_0_7():
    print("=" * 60)
    print("MarkRender v1.0.7 Feature Showcase")
    print("=" * 60)
    print()

    # 1. Improved Hyperlinks & Word Wrapping
    print("--- 1. Robust Hyperlinks & Word Wrapping ---")
    markdown_links = """
This is a standard link: [GitHub Repository](https://github.com/Praneeth-Gandodi/markrender)
In modern terminals, the text above is clickable (OSC 8).

Here is a very long paragraph to demonstrate **word wrapping**. Notice how long words like 
'Supercalifragilisticexpialidocious' or 'Antidisestablishmentarianism' are handled gracefully 
without being cut in half at the end of the line. We ensure that the terminal width is 
respected and content stays readable.
"""
    renderer = MarkdownRenderer(width=60)
    renderer.render(markdown_links)
    renderer.finalize()
    print()

    # 2. File Tree Rendering
    print("--- 2. File Tree Rendering ---")
    tree_markdown = """
You can now render beautiful file trees using the `tree` or `file-tree` code blocks:

```tree
markrender/
├── markrender/
│   ├── __init__.py
│   ├── cli.py
│   ├── colors.py
│   ├── config.py
│   ├── formatters.py
│   ├── parser.py
│   ├── renderer.py
│   └── themes.py
├── tests/
│   └── test_renderer.py
├── pyproject.toml
└── README.md
```
"""
    renderer = MarkdownRenderer()
    renderer.render(tree_markdown)
    renderer.finalize()
    print()

    # 3. Dim Mode (Thinking Mode)
    print("--- 3. Dim Mode (Thinking Mode) ---")
    print("(Useful for LLM 'thought' processes or background information)")
    dim_markdown = """
> [!INFO] This content is rendered in Dim Mode.
> It uses reduced colors and dimmed text to look less prominent.
> 
> - Sub-point 1
> - Sub-point 2
> 
> ```python
> def thinking():
>     return "This code is also dimmed"
> ```
"""
    renderer = MarkdownRenderer(dim_mode=True)
    renderer.render(dim_markdown)
    renderer.finalize()
    print()

    # 4. Improved Nested Lists
    print("--- 4. Improved Nested Lists ---")
    list_markdown = """
1. Level 1 - Item A
   - Level 2 - Subitem 1
   - Level 2 - Subitem 2
     1. Level 3 - Deep Item i
     2. Level 3 - Deep Item ii
        - Level 4 - Very Deep
2. Level 1 - Item B
   * Another subitem
"""
    renderer = MarkdownRenderer()
    renderer.render(list_markdown)
    renderer.finalize()
    print()

    print("=" * 60)
    print("Showcase Complete!")
    print("=" * 60)

if __name__ == "__main__":
    demonstrate_v1_0_7()
