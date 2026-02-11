# MarkRender 🎨

**A professional terminal markdown renderer built for streaming LLM responses.**

MarkRender is a Python library designed to bring beautifully rendered markdown directly to your terminal. It's especially good for displaying streaming output from large language models, ensuring a smooth, flicker-free experience with rich formatting and syntax highlighting.

## ✨ Features You'll Love

*   **Streaming Optimized**: Renders markdown chunks as they arrive, perfect for LLM interactions.
*   **Gorgeous Themes**: Comes with several built-in color themes to match your terminal aesthetic.
*   **Smart Syntax Highlighting**: Powered by Pygments, it makes your code blocks pop.
*   **Full Markdown Support**: Handles everything from headings and lists to tables, checkboxes, emojis, and links.

## 🚀 Get Started

### Installation

It's super easy to get MarkRender up and running:

```bash
pip install git+https://github.com/Praneeth-Gandodi/markrender.git
```

### Quick Usage

Here's how to render a simple markdown string:

```python
from markrender import MarkdownRenderer

renderer = MarkdownRenderer()
markdown_text = """
# Welcome to MarkRender!

This is **bold** text and this is *italic*.

Here's some `inline code`.

- [x] Task completed
- [ ] Another task

```python
def example_code():
    print("Hello, MarkRender!")
```
"""
renderer.render(markdown_text)
renderer.finalize() # Don't forget to finalize to flush any remaining content!
```

### Rendering Streaming Content

MarkRender shines when dealing with streaming text, like responses from an LLM:

```python
from markrender import MarkdownRenderer
import time # For simulating delay

renderer = MarkdownRenderer(theme='dracula', line_numbers=True)

streaming_text = """
# Quantum Physics ⚛️

Quantum mechanics is a fundamental theory in physics that describes the properties of nature at the scale of atoms and subatomic particles.

## Key Concepts

1. **Superposition**: Particles can exist in multiple states simultaneously.
2. **Entanglement**: Two or more particles become linked, sharing the same fate.

```python
# Simple quantum simulation idea
def measure_qubit():
    # In a real scenario, this involves quantum hardware
    return "0" if time.time() % 2 == 0 else "1"

print(f"Qubit measured: {measure_qubit()}")
```

> [!NOTE]
> This is a simplified explanation. Quantum physics is much deeper!

For more info, check out [Wikipedia](https://en.wikipedia.org/wiki/Quantum_mechanics).
"""

# Simulate streaming by chunking the text
chunk_size = 50
for i in range(0, len(streaming_text), chunk_size):
    chunk = streaming_text[i:i + chunk_size]
    renderer.render(chunk)
    time.sleep(0.05) # Small delay to simulate real streaming

renderer.finalize()
```

## 🎨 Customize Your Output

MarkRender is designed to be flexible. You can tailor its appearance to fit your needs:

*   **`theme`**: Choose from built-in themes like `'github-dark'` (default), `'monokai'`, `'dracula'`, `'nord'`, `'one-dark'`, `'solarized-dark'`, or `'solarized-light'`.
    ```python
    renderer = MarkdownRenderer(theme='monokai')
    ```
*   **`code_background`**: Set to `True` to give code blocks a distinct background color. (Default: `False`)
    ```python
    renderer = MarkdownRenderer(code_background=True)
    ```
*   **`line_numbers`**: Display line numbers in your code blocks. (Default: `True`)
    ```python
    renderer = MarkdownRenderer(line_numbers=False) # Turn off line numbers
    ```
*   **`inline_code_color`**: Override the theme's default color for `inline code` snippets. You can use standard ANSI color codes or custom RGB values.
    ```python
    from markrender.colors import rgb
    renderer = MarkdownRenderer(inline_code_color=rgb(255, 100, 200)) # A custom pink!
    ```
*   **`width`**: Manually set the terminal width in characters. By default, MarkRender auto-detects your terminal's width.
    ```python
    renderer = MarkdownRenderer(width=120)
    ```

## ⚠️ A Note on Table Rendering

MarkRender uses the `rich` library for table rendering, which is excellent at adapting tables to your terminal's width. While we strive for perfect output, displaying very complex or wide tables in a narrow terminal environment can sometimes lead to aggressive text wrapping in cells and headers. This is a common challenge in terminal UIs, but MarkRender ensures all content is displayed (wrapped, not truncated) even if it means visually "tall" rows. For the best table appearance, a wider terminal window is always recommended!

## 🤝 Contributing

We welcome contributions! Feel free to open issues or pull requests on our [GitHub repository](https://github.com/Praneeth-Gandodi/markrender).

## 📄 License

MarkRender is released under the MIT License. See the [LICENSE](LICENSE) file for more details.
