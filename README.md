# MarkRender 🎨

**A professional terminal markdown renderer built for streaming LLM responses.**

MarkRender is a Python library designed to bring beautifully rendered markdown directly to your terminal. It's especially good for displaying streaming output from large language models, ensuring a smooth, flicker-free experience with rich formatting and syntax highlighting.

## ✨ Features You'll Love

* **Streaming Optimized**: Renders markdown chunks as they arrive, perfect for LLM interactions.
* **Gorgeous Themes**: Comes with several built-in color themes to match your terminal aesthetic.
* **Smart Syntax Highlighting**: Powered by Pygments, it makes your code blocks pop.
* **Full Markdown Support**: Handles everything from headings and lists to tables, checkboxes, emojis, and links.

## 🚀 Get Started

### Installation

It's super easy to get MarkRender up and running:

```bash
pip install git+https://github.com/Praneeth-Gandodi/markrender.git
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

## Available themes

* github-dark
* monokai
* dracula
* nord
* one-dark
* solarized-dark
* solarized-light

How to change theme

```python

from markrender import MarkdownRenderer

renderer = MarkdownRenderer(
    theme='monokai',         # Set the color style
    line_numbers=True,       # Show numbers next to code lines
    code_background=True,    # Add a background color to code blocks
    force_color=True         # Always show colors
)

```

---

> [!Note] A Note on Table Rendering
MarkRender uses the `rich` library for table rendering, which is excellent at adapting tables to your terminal's width. While we strive for perfect output, displaying very complex or wide tables in a narrow terminal environment can sometimes lead to aggressive text wrapping in cells and headers. This is a common challenge in terminal UIs, but MarkRender ensures all content is displayed (wrapped, not truncated) even if it means visually "tall" rows. For the best table appearance, a wider terminal window is always recommended!

## 🤝 Contributing

We welcome contributions! Feel free to open issues or pull requests on our [GitHub repository](https://github.com/Praneeth-Gandodi/markrender).

## 📄 License

MarkRender is released under the MIT License. See the [LICENSE](LICENSE) file for more details.
