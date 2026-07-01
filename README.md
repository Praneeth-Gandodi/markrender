# MarkRender

**Professional Terminal Markdown Renderer for Streaming LLM Responses**

MarkRender is a Python library that renders markdown in terminals, designed for streaming LLM responses. It provides syntax highlighting, multiple color themes, and supports markdown features without flickering.

## Features

- **Streaming Support** - Designed for chunk-by-chunk LLM response rendering
- **7 Themes** - github-dark, monokai, dracula, nord, one-dark, solarized-dark, solarized-light
- **Syntax Highlighting** - Powered by Pygments with 500+ languages
- **Dim Mode** - Render content in dimmed/reduced colors for "thinking" sections
- **Theme Preview** - Preview all themes with sample content via CLI
- **Line Numbers** - Optional line numbers in code blocks
- **Tables** - Table rendering with borders and overflow truncation
- **Checkboxes** - Task list support
- **Emoji Support** - Converts `:emoji_name:` to actual emojis
- **Links** - Styled hyperlinks with URLs
- **Full Markdown** - Headings, lists, blockquotes, horizontal rules, alerts, and more
- **Force Color** - Force color output even in non-tty terminals
- **Customizable** - Custom colors, backgrounds, and formatting options
- **Python 3.7+** - Compatible with Python 3.7 and above

## Installation

```bash
pip install git+https://github.com/Praneeth-Gandodi/markrender.git
```

Or install from source:

```bash
git clone https://github.com/Praneeth-Gandodi/markrender.git
cd markrender
pip install -e .
```

## Quick Start

````python
from markrender import MarkdownRenderer

# Create renderer with default theme
renderer = MarkdownRenderer()

# Render markdown content
markdown_text = """
# Hello World

This is **bold** and this is *italic*.

```python
def hello():
    print("Hello from MarkRender!")
```

## Features
- Item 1
- Item 2
- [x] Completed task
- [ ] Pending task
"""

renderer.render(markdown_text)
renderer.finalize()
````

### Streaming LLM Responses

Perfect for rendering streaming responses from LLM APIs:

```python
from markrender import MarkdownRenderer
from openai import OpenAI

client = OpenAI()
renderer = MarkdownRenderer(theme='github-dark')

stream = client.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": "Explain quantum computing"}],
    stream=True
)

for chunk in stream:
    content = chunk.choices[0].delta.content
    if content:
        renderer.render(content)

renderer.finalize()
```

### Dim Mode

Use dim mode for "thinking" sections or less prominent content:

```python
from markrender import MarkdownRenderer

renderer = MarkdownRenderer()

# Normal rendering
renderer.render("This is **normal** content")

# Dim/reduced color rendering
renderer.render("This content is dimmed and less prominent", dim_mode=True)
```

### Theme Preview

Preview all available themes from the CLI:

```bash
markrender --preview-themes
```

## Themes

MarkRender includes 7 professional color themes:

```python
themes = [
    'github-dark',      # GitHub's dark theme (default)
    'monokai',          # Popular Monokai theme
    'dracula',          # Dracula theme
    'nord',             # Nord color palette
    'one-dark',         # Atom One Dark
    'solarized-dark',   # Solarized Dark
    'solarized-light'   # Solarized Light
]

renderer = MarkdownRenderer(theme='dracula')
```

List available themes:

```bash
markrender --list-themes
```

## Configuration

### Python API

```python
from markrender import MarkdownRenderer
from markrender.colors import rgb

renderer = MarkdownRenderer(
    theme='monokai',                       # Color theme
    code_background=False,                 # Show background in code blocks
    line_numbers=True,                     # Show line numbers in code
    inline_code_color=rgb(255, 100, 200),  # Custom inline code color
    width=100,                             # Terminal width (auto-detect by default)
    force_color=False,                     # Force color output
    stream_code=True                       # Stream code lines as they arrive
)
```

### Parameters

- **theme** (str): Color theme name (default: `'github-dark'`)
- **code_background** (bool): Show background in code blocks (default: `False`)
- **line_numbers** (bool): Show line numbers in code blocks (default: `True`)
- **inline_code_color** (str): Custom ANSI color code for inline code (default: theme default)
- **width** (int): Terminal width in characters (default: auto-detect)
- **force_color** (bool): Force color output even if terminal does not support it (default: `False`)
- **stream_code** (bool): Render code lines as they arrive instead of buffering (default: `True`)
- **output** (file): Output stream (default: `sys.stdout`)

### CLI Usage

```bash
markrender README.md
markrender --theme dracula file.md
cat file.md | markrender
markrender --preview-themes
markrender --list-themes
markrender --no-line-numbers --code-background file.md
markrender --width 80 --force-color file.md
```

### Config File

MarkRender supports TOML configuration files. Place a `.markrender.toml` in your current directory or `~/.markrender/config.toml`:

```toml
[theme]
name = "github-dark"

[rendering]
code_background = false
line_numbers = true

[output]
# width = 80
force_color = false

[features]
stream_code = true
```

## Supported Markdown Features

### Headings
```markdown
# H1 Heading
## H2 Heading
### H3 Heading
#### H4 Heading
##### H5 Heading
###### H6 Heading
```

### Code Blocks
````markdown
```python
def example():
    return "Syntax highlighted!"
```
````

### Inline Code
```markdown
Use `inline code` for short snippets.
```

### Tables
```markdown
| Feature | Supported |
|---------|-----------|
| Tables  | Yes       |
| Borders | Yes       |
```

### Lists
```markdown
- Unordered item 1
- Unordered item 2
  - Nested item

1. Ordered item 1
2. Ordered item 2
```

### Checkboxes
```markdown
- [x] Completed task
- [ ] Pending task
```

### Blockquotes
```markdown
> This is a blockquote
> It can span multiple lines
```

### Alerts (GitHub-flavored)
```markdown
> [!NOTE]
> Useful information users should know

> [!TIP]
> Helpful advice

> [!IMPORTANT]
> Key information

> [!WARNING]
> Urgent information

> [!CAUTION]
> Potential negative consequences
```

### Links
```markdown
[Link text](https://example.com)
```

### Text Formatting
```markdown
**Bold text**
*Italic text*
***Bold and italic***
~~Strikethrough~~
```

### Emojis
```markdown
Hello :wave: Let's :rocket: go!
```

### Horizontal Rules
```markdown
---
```

## Use Cases

- **AI Chat Applications** - Render LLM responses in CLI tools
- **Documentation Viewers** - Display markdown documentation in terminal
- **Code Review Tools** - Show code diffs and comments
- **Note-Taking Apps** - Terminal-based markdown note viewers
- **Log Viewers** - Render structured logs with markdown

## Development

### Setup Development Environment

```bash
git clone https://github.com/Praneeth-Gandodi/markrender.git
cd markrender
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -e ".[dev]"
```

### Run Tests

```bash
pytest tests/ -v
pytest tests/ --cov=markrender --cov-report=html --cov-report=term
```

### Run Examples

```bash
python examples/basic_usage.py
python examples/streaming_demo.py
python examples/theme_showcase.py
```

## License

MIT License - see [LICENSE](LICENSE) file for details.
