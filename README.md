# MarkRender 🎨

**A professional terminal markdown renderer built for streaming LLM responses.**

MarkRender is a Python library designed to bring beautifully rendered markdown directly to your terminal. It's especially good for displaying streaming output from large language models, ensuring a smooth, flicker-free experience with rich formatting and syntax highlighting.

## ✨ Features You'll Love

* **Streaming Optimized**: Renders markdown chunks as they arrive, perfect for LLM interactions.
* **Gorgeous Themes**: Comes with several built-in color themes to match your terminal aesthetic.
* **Smart Syntax Highlighting**: Powered by Pygments, it makes your code blocks pop.
* **Full Markdown Support**: Handles everything from headings and lists to tables, checkboxes, emojis, and links with robust streaming support.
* **Cross-Platform**: Works on Windows, macOS, and Linux.

## 🚀 Get Started

### Installation

It's super easy to get MarkRender up and running:

```bash
pip install git+https://github.com/Praneeth-Gandodi/markrender.git
```

Or, for development, clone the repository and install in editable mode:
```bash
git clone https://github.com/Praneeth-Gandodi/markrender.git
cd markrender
pip install -e .
```

### Quick Usage

Here's how to render a simple markdown string

```python
from markrender import MarkdownRenderer

renderer = MarkdownRenderer() 

markdown_text = """
# Project Title  
This is a comprehensive markdown example that demonstrates various features.  
It includes headers, lists, links, images, and code blocks.  

## Subsection Explanation  
- **Headers** are defined using `#` symbols.  
- **Lists** can be ordered or unordered.  
- **Links** use the syntax: `[text](url)`.  
- **Images** are added via `![alternative text](path)`.  

---

### Installation 
To get started, run the following command in your terminal:  
`pip install markrender`

### Feature Comparison
| Feature | Syntax |
| :--- | :--- |
| Bold | **text** |
| Italic | *text* |
| Inline Code | `code` |

> **Note:** Ensure your renderer is finalized after use to prevent memory leaks.
"""

renderer.render(markdown_text)
renderer.finalize()
```

How to render streaming api responses

```python
from openai import OpenAI

renderer = MarkdownRenderer(theme='github-dark', line_numbers=True)

API_KEY = # Your openai api key

client = OpenAI(api_key=API_KEY)

stream = client.chat.completions.create(
    model="openai/gpt-oss-120b",
    messages=[
    {
        "role": "system",
        "content": "You are a highly capable AI assistant that answers clearly and concisely."
    },
    {
        "role": "user",
        "content": "Whats the difference between C and C++?"
    }
    ],
    stream=True
)
for chunk in stream:
    data = chunk.choices[0].delta.content
    if data: 
        renderer.render(data)

renderer.finalize() 
```

## 🎨 Advanced Configuration

You can customize the renderer's appearance and behavior with the following parameters:

```python
from markrender import MarkdownRenderer

renderer = MarkdownRenderer(
    theme='monokai',         # Set the color style
    line_numbers=True,       # Show numbers next to code lines
    code_background=True,    # Add a background color to code blocks
    force_color=True,        # Always show colors
    stream_code=True         # Render code blocks line-by-line
)
```

### Non-Streaming Code Blocks

If you prefer to render code blocks all at once after the entire block has been received, you can set `stream_code=False`. This is useful if you want to avoid seeing incomplete code blocks during streaming.

```python
renderer = MarkdownRenderer(stream_code=False)
```

## Available themes

* github-dark
* monokai
* dracula
* nord
* one-dark
* solarized-dark
* solarized-light


---

## 📊 Table Rendering Excellence

MarkRender provides robust table rendering powered by the `rich` library. Tables are beautifully formatted with proper alignment, borders, and theme-appropriate colors. The renderer handles streaming edge cases gracefully, ensuring tables render correctly even when content arrives in chunks.

## 🤝 Contributing

We welcome contributions! Feel free to open issues or pull requests on our [GitHub repository](https://github.com/Praneeth-Gandodi/markrender).

## 📄 License

MarkRender is released under the MIT License. See the [LICENSE](LICENSE) file for more details.
