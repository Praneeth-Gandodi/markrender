# MarkRender

MarkRender is a Python library for rendering Markdown in the terminal. It is designed to be highly customizable and is particularly well-suited for streaming content, such as responses from Large Language Models (LLMs).

## Key Features

- **Streaming Support**: MarkRender can process and render Markdown content as it arrives, providing a smooth and responsive experience for dynamic content.
- **Syntax Highlighting**: Code blocks are highlighted using the powerful Pygments library, supporting a wide range of languages.
- **Theming**: Choose from a variety of built-in themes to customize the appearance of your rendered output.
- **Table Rendering**: Tables are rendered with proper formatting and alignment, powered by the `rich` library.
- **Advanced Markdown Support**: Highlights, footnotes, definition lists, progress bars, nested lists, and image placeholders.
- **CLI Interface**: Render markdown files directly from the command line.
- **Configuration**: Support for TOML configuration files.
- **Cross-Platform**: Works on Windows, macOS, and Linux.

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

- `theme`: The color theme to use for syntax highlighting.
- `line_numbers`: Whether to display line numbers in code blocks.
- `code_background`: Whether to add a background color to code blocks.
- `force_color`: If `True`, forces color output even if the terminal does not appear to support it.
- `stream_code`: If `False`, code blocks are rendered all at once at the end, rather than line by line.
- `use_config`: If `True` (default), loads configuration from config file.

## Available Themes

- `github-dark`
- `monokai`
- `dracula`
- `nord`
- `one-dark`
- `solarized-dark`
- `solarized-light`

## Advanced Features

### Highlighted Text

Use `==text==` syntax to highlight text:

```python
from markrender import MarkdownRenderer

renderer = MarkdownRenderer()

markdown_text = """
# Highlighting Example

This is normal text with ==highlighted text== for emphasis.

You can also combine with other formatting: ==**bold highlight**== or ==*italic highlight*==.
"""

renderer.render(markdown_text)
renderer.finalize()
```

### Nested Lists

MarkRender supports deeply nested lists:

```python
from markrender import MarkdownRenderer

renderer = MarkdownRenderer()

markdown_text = """
# Nested Lists Example

## Unordered Lists

- Item 1
  - Nested item 1.1
    - Deep nested item 1.1.1
  - Nested item 1.2
- Item 2
  - Nested item 2.1

## Ordered Lists

1. First item
   1. Sub-item 1
   2. Sub-item 2
2. Second item
   1. Sub-item 1
"""

renderer.render(markdown_text)
renderer.finalize()
```

### Progress Bars

Use `- [X%]` syntax to show task progress with visual progress bars:

```python
from markrender import MarkdownRenderer

renderer = MarkdownRenderer()

markdown_text = """
# Task Progress

- [0%] Not started
- [25%] In progress
- [50%] Halfway done
- [75%] Almost complete
- [100%] Completed
"""

renderer.render(markdown_text)
renderer.finalize()
```

Progress bars are color-coded:
- Red: 0-24%
- Orange: 25-49%
- Yellow: 50-74%
- Green: 75-99%
- Checkmark: 100%

### Image Placeholders

Since terminals cannot display actual images, MarkRender renders image placeholders:

```python
from markrender import MarkdownRenderer

renderer = MarkdownRenderer()

markdown_text = """
# Image Example

Here is an image:

![Architecture Diagram](https://example.com/diagram.png)

Another image: ![Logo](https://example.com/logo.jpg)
"""

renderer.render(markdown_text)
renderer.finalize()
```

Images are displayed as bordered boxes with alt text and URL.

### Footnotes

Add footnotes to your documents:

```python
from markrender import MarkdownRenderer

renderer = MarkdownRenderer()

markdown_text = """
# Footnotes Example

This is a statement with a footnote reference.[^1]

Here is another statement with a different footnote.[^note]

[^1]: This is the first footnote content. It can contain multiple sentences.

[^note]: This is a named footnote. You can use any identifier here.
"""

renderer.render(markdown_text)
renderer.finalize()
```

Footnotes are collected and displayed at the end of the document.

### Definition Lists

Use `Term : Definition` syntax for glossaries and definitions:

```python
from markrender import MarkdownRenderer

renderer = MarkdownRenderer()

markdown_text = """
# Definition Lists Example

**Python** : A high-level programming language known for its simplicity.

**API** : Application Programming Interface, allows software components to communicate.

**Markdown** : A lightweight markup language for creating formatted text.
"""

renderer.render(markdown_text)
renderer.finalize()
```

## CLI Interface

MarkRender includes a command-line interface for rendering markdown files:

```bash
# Render a markdown file
markrender README.md

# Use a specific theme
markrender --theme dracula file.md

# Disable line numbers
markrender --no-line-numbers file.md

# Enable code background
markrender --code-background file.md

# Force color output
markrender --force-color file.md

# List available themes
markrender --list-themes

# Render from stdin
cat file.md | markrender
```

### CLI Options

| Option | Description |
|--------|-------------|
| `-t, --theme` | Syntax highlighting theme (default: github-dark) |
| `--no-line-numbers` | Disable line numbers in code blocks |
| `--code-background` | Enable background color in code blocks |
| `--width` | Set terminal width (default: auto-detect) |
| `--no-stream-code` | Render code blocks all at once |
| `--force-color` | Force color output |
| `--list-themes` | List available themes and exit |
| `-v, --version` | Show version information |

## Configuration

MarkRender supports configuration via TOML files. Create a config file at:

- `~/.markrender/config.toml` (home directory)
- `.markrender.toml` (current directory)

### Example Configuration

```toml
# MarkRender Configuration

[theme]
name = "github-dark"

[rendering]
code_background = false
line_numbers = true

[output]
# width = 80  # Uncomment to set fixed width
force_color = false

[features]
stream_code = true
```

### Creating Default Config

```python
from markrender import create_default_config

# Create default config file at ~/.markrender/config.toml
create_default_config()
```

## Custom Themes

Register your own custom themes:

```python
from markrender import register_theme, MarkdownRenderer

custom_theme = {
    'name': 'my-custom-theme',
    'pygments_style': 'monokai',
    'heading_colors': {
        1: '#ff0000',
        2: '#00ff00',
        3: '#0000ff',
        4: '#ffff00',
        5: '#00ffff',
        6: '#ff00ff',
    },
    'inline_code': '#123456',
    'link': '#654321',
    'blockquote_border': '#aaaaaa',
    'table_border': '#bbbbbb',
    'checkbox_unchecked': '#cccccc',
    'checkbox_checked': '#dddddd',
    'hr': '#eeeeee',
    'highlight': '#ffffff',
    'list_marker': '#111111',
    'table_header': '#222222',
}

register_theme('my-custom-theme', custom_theme)

# Use the custom theme
renderer = MarkdownRenderer(theme='my-custom-theme')
```

## Complete Example

Here is a comprehensive example demonstrating multiple features:

````python
from markrender import MarkdownRenderer

renderer = MarkdownRenderer(
    theme='github-dark',
    line_numbers=True,
    code_background=False
)

markdown_content = """
# Complete MarkRender Demo

## Text Formatting

This document demonstrates ==highlighted text==, **bold**, *italic*, and `inline code`.

## Nested Lists

- Main item 1
  - Sub-item 1.1
    - Deep item 1.1.1
  - Sub-item 1.2
- Main item 2
  1. Ordered sub-item
  2. Another ordered sub-item

## Progress Tracking

- [0%] Planning
- [25%] Design
- [50%] Implementation
- [75%] Testing
- [100%] Deployment

## Code Example

```python
def greet(name):
    return f"Hello, {name}!"

print(greet("World"))
```

## Definition List

**MarkRender** : A terminal markdown renderer for Python.

**Rich** : A library for rich terminal output.

## Footnotes

This is an important point.[^1]

[^1]: This footnote provides additional context.

## Image Reference

See the diagram below:

![System Architecture](https://example.com/arch.png)

---

End of demo.
"""

renderer.render(markdown_content)
renderer.finalize()
````

## API Reference

### MarkdownRenderer

```python
from markrender import MarkdownRenderer

renderer = MarkdownRenderer(
    theme='github-dark',      # Theme name
    code_background=False,    # Show code block background
    inline_code_color=None,   # Custom inline code color
    line_numbers=True,        # Show line numbers
    width=None,               # Terminal width (auto-detect if None)
    output=None,              # Output file (sys.stdout if None)
    force_color=False,        # Force color output
    stream_code=True,         # Stream code line by line
    use_config=True           # Load from config file
)

renderer.render(markdown_text)  # Render markdown content
renderer.finalize()             # Finalize and flush output
```

### Utility Functions

```python
from markrender import list_themes, get_theme, register_theme, create_default_config

# List available themes
themes = list_themes()

# Get theme configuration
theme = get_theme('github-dark')

# Register custom theme
register_theme('my-theme', theme_config)

# Create default config file
create_default_config()
```

## Contributing

Contributions are welcome! Please feel free to open an issue or submit a pull request on the [GitHub repository](https://github.com/Praneeth-Gandodi/markrender).

## License

MarkRender is distributed under the MIT License. See the `LICENSE` file for more details.
