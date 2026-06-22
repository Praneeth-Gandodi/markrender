# MarkRender 🎨

**Professional Terminal Markdown Renderer for Streaming LLM Responses**

MarkRender is a production-ready Python library that beautifully renders markdown in terminals, specifically designed for streaming LLM responses. It provides syntax highlighting, multiple color themes, and supports all essential markdown features without flickering or performance issues.

> [!IMPORTANT]
> This project is currently in **active development**. While it is designed for production-ready environments, we are continuously iterating to improve performance and stability.

## ✨ Features

- 🎯 **Streaming Support** - Designed for chunk-by-chunk LLM response rendering
- 🎨 **7 Beautiful Themes** - github-dark, monokai, dracula, nord, one-dark, solarized-dark, solarized-light
- 💻 **Syntax Highlighting** - Powered by Pygments with 500+ languages
- 🔢 **Line Numbers** - Optional line numbers in code blocks
- 📊 **Tables** - Beautiful table rendering with borders
- ✅ **Checkboxes** - Task list support (☐/☑)
- 😊 **Emoji Support** - Converts `:emoji_name:` to actual emojis
- 🔗 **Links** - Styled hyperlinks with URLs
- 📝 **Full Markdown** - Headings, lists, blockquotes, horizontal rules, and more
- ⚡ **Fast & Smooth** - No flickering, instant rendering
- 🐍 **Python 3.7+** - Compatible with Python 3.7 and above
- 🎛️ **Customizable** - Custom colors, backgrounds, and formatting options

## 🚀 Installation

```bash
pip install git+https://github.com/Praneeth-Gandodi/markrender.git
```

Or install from source:

```bash
git clone https://github.com/Praneeth-Gandodi/markrender.git
cd markrender
pip install -e .
```

## 📖 Quick Start

### Basic Usage

```python
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
```

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

## 🎨 Themes

MarkRender includes 7 professional color themes:

```python
# Available themes
themes = [
    'github-dark',      # GitHub's dark theme (default)
    'monokai',          # Popular Monokai theme
    'dracula',          # Dracula theme
    'nord',             # Nord color palette
    'one-dark',         # Atom One Dark
    'solarized-dark',   # Solarized Dark
    'solarized-light'   # Solarized Light
]

# Use a theme
renderer = MarkdownRenderer(theme='dracula')
```

## ⚙️ Configuration

Customize the renderer to your needs:

```python
from markrender import MarkdownRenderer
from markrender.colors import rgb

renderer = MarkdownRenderer(
    theme='monokai',                    # Color theme
    code_background=False,              # Show background in code blocks
    line_numbers=True,                  # Show line numbers in code
    inline_code_color=rgb(255, 100, 200),  # Custom inline code color
    width=100                           # Terminal width (auto-detect by default)
)
```

### Parameters

- **theme** (str): Color theme name (default: `'github-dark'`)
- **code_background** (bool): Show background in code blocks (default: `False`)
- **line_numbers** (bool): Show line numbers in code blocks (default: `True`)
- **inline_code_color** (str): Custom ANSI color code for inline code (default: theme's purple variant)
- **width** (int): Terminal width in characters (default: auto-detect)
- **output** (file): Output stream (default: `sys.stdout`)

## 📚 Supported Markdown Features

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
| Tables  | ✓         |
| Borders | ✓         |
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

### Links
```markdown
[Link text](https://example.com)
```

### Text Formatting
```markdown
**Bold text**
*Italic text*
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

## 🎯 Use Cases

- **AI Chat Applications** - Render LLM responses in CLI tools
- **Documentation Viewers** - Display markdown documentation in terminal
- **Code Review Tools** - Show code diffs and comments
- **Note-Taking Apps** - Terminal-based markdown note viewers
- **Log Viewers** - Render structured logs with markdown

## 🤝 Comparison with Alternatives

Unlike `rich.Markdown` which can flicker during streaming and has higher computational overhead, MarkRender is specifically optimized for:

- ✅ Smooth streaming without redrawing
- ✅ Lower CPU usage
- ✅ GitHub-style markdown rendering
- ✅ Professional code block styling like Claude CLI, Gemini CLI, and Qwen CLI
- ✅ Customizable themes and colors

## 🧪 Development

### Setup Development Environment

```bash
# Clone repository
git clone https://github.com/Praneeth-Gandodi/markrender.git
cd markrender

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -e ".[dev]"
```

### Run Tests

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=markrender --cov-report=html --cov-report=term
```

### Run Examples

```bash
# Basic usage
python examples/basic_usage.py

# Streaming demo
python examples/streaming_demo.py

# Theme showcase
python examples/theme_showcase.py
```

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Pygments** - Syntax highlighting engine
- **emoji** - Emoji rendering support
