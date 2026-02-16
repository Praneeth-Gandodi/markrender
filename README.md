# MarkRender

MarkRender is a Python library for rendering Markdown in the terminal. It is designed to be highly customizable and is particularly well-suited for streaming content, such as responses from Large Language Models (LLMs).

## Key Features

*   **Streaming Support**: MarkRender can process and render Markdown content as it arrives, providing a smooth and responsive experience for dynamic content.
*   **Syntax Highlighting**: Code blocks are highlighted using the powerful Pygments library, supporting a wide range of languages.
*   **Theming**: Choose from a variety of built-in themes to customize the appearance of your rendered output.
*   **Table Rendering**: Tables are rendered with proper formatting and alignment, powered by the `rich` library.
*   **Markdown Compatibility**: Supports a wide range of Markdown features, including headings, lists, blockquotes, and more.
*   **Cross-Platform**: Works on Windows, macOS, and Linux.

## Installation

You can install MarkRender using pip:

```bash
pip install markrender
```

For development, you can clone the repository and install it in editable mode:

```bash
git clone https://github.com/Praneeth-Gandodi/markrender.git
cd markrender
pip install -e .
```

## Basic Usage

To render a Markdown string, create a `MarkdownRenderer` instance and use its `render` method:

````python
from markrender import MarkdownRenderer

renderer = MarkdownRenderer()

markdown_text = """
# Example Document

This is a sample Markdown document to demonstrate the capabilities of MarkRender.

## Text Formatting

You can use various text formatting options, such as:

- **Bold text**
- *Italic text*
- `Inline code`

## Code Blocks

```python
def hello_world():
    print("Hello, from MarkRender!")
```

## Tables

| Feature         | Supported |
| --------------- | :-------: |
| Streaming       |    Yes    |
| Syntax Highlighting |    Yes    |
| Theming         |    Yes    |

"""

renderer.render(markdown_text)
renderer.finalize()
````

## Streaming Usage

MarkRender is ideal for rendering content that arrives in chunks, such as from an API response. The `render` method can be called multiple times with partial content.

````python
import time
from markrender import MarkdownRenderer

renderer = MarkdownRenderer()

markdown_stream = [
    "# Streaming Example\n\n",
    "This text is being rendered in chunks.\n\n",
    "```python\n",
    "for i in range(5):\n",
    "    print(i)\n",
    "```\n",
]

for chunk in markdown_stream:
    renderer.render(chunk)
    time.sleep(0.5)

renderer.finalize()
````

## Customization

The `MarkdownRenderer` can be customized with various options:

```python
from markrender import MarkdownRenderer

renderer = MarkdownRenderer(
    theme='monokai',
    line_numbers=True,
    code_background=True,
    force_color=True,
    stream_code=True
)
```

**Available Options:**

*   `theme`: The color theme to use for syntax highlighting.
*   `line_numbers`: Whether to display line numbers in code blocks.
*   `code_background`: Whether to add a background color to code blocks.
*   `force_color`: If `True`, forces color output even if the terminal does not appear to support it.
*   `stream_code`: If `False`, code blocks are rendered all at once at the end, rather than line by line.

## Available Themes

*   `github-dark`
*   `monokai`
*   `dracula`
*   `nord`
*   `one-dark`
*   `solarized-dark`
*   `solarized-light`

## Contributing

Contributions are welcome! Please feel free to open an issue or submit a pull request on the [GitHub repository](https://github.com/Praneeth-Gandodi/markrender).

## License

MarkRender is distributed under the MIT License. See the `LICENSE` file for more details.
