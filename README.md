# MarkRender

**Professional Terminal Markdown Renderer for Streaming LLM Responses**

MarkRender renders markdown in the terminal. It is built for streaming output, so you can hand it a complete string or feed it chunks from an LLM as they arrive. Syntax highlighting, themes, tables, and the rest work the same either way, without reprinting content that is already on screen.

## Features

- **Streaming Support** - Designed for chunk-by-chunk LLM response rendering
- **7 Themes** - github-dark, monokai, dracula, nord, one-dark, solarized-dark, solarized-light
- **Syntax Highlighting** - Powered by Pygments with 500+ languages
- **Dim Mode** - Render "thinking" content in a single muted gray
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

MarkRender is on PyPI:

```bash
pip install markrender
```

That installs the library and the `markrender` command. Check that it worked:

```bash
markrender --version
```

Upgrade an existing install with:

```bash
pip install --upgrade markrender
```

If you want to work on MarkRender itself, clone the repo and install it in editable mode instead:

```bash
git clone https://github.com/Praneeth-Gandodi/markrender.git
cd markrender
pip install -e ".[dev]"
```

## Command Line

Render a file:

```bash
markrender README.md
```

Read markdown from stdin:

```bash
cat notes.md | markrender
```

On PowerShell:

```powershell
Get-Content notes.md -Raw | markrender
```

Pick a theme:

```bash
markrender --theme dracula notes.md
```

Adjust code blocks:

```bash
markrender --no-line-numbers notes.md
markrender --code-background notes.md
markrender --no-stream-code notes.md
```

Set a fixed width when the terminal reports the wrong size, or when the output goes somewhere else:

```bash
markrender --width 80 notes.md
```

Force color when piping into another program, a log file, or CI:

```bash
markrender --force-color notes.md | less -R
```

List the theme names:

```bash
markrender --list-themes
```

Preview every theme with sample content:

```bash
markrender --preview-themes
```

Running `markrender` with no file and nothing piped in prints an error and exits.

### Options

| Option | Description |
|--------|-------------|
| `--theme NAME` | Color theme (default: `github-dark`) |
| `--no-line-numbers` | Hide line numbers in code blocks |
| `--code-background` | Show a background behind code blocks |
| `--width N` | Wrap at a fixed width instead of the terminal width |
| `--no-stream-code` | Render code blocks in one pass instead of line by line |
| `--force-color` | Emit colors even when the output is not a terminal |
| `--list-themes` | Print available themes and exit |
| `--preview-themes` | Render sample markdown in every theme and exit |
| `-v`, `--version` | Print the version and exit |

CLI flags override values from a config file. See [Configuration](#configuration).

## Python API

### Render a string

````python
from markrender import MarkdownRenderer

renderer = MarkdownRenderer()

markdown = """
# Hello

Some **bold** text, some *italic* text, and `inline code`.

```python
def hello():
    print("Hello from MarkRender!")
```

- A list item
- [x] A finished task
- [ ] A pending task
"""

renderer.render(markdown)
renderer.finalize()
````

`render()` writes output as it parses, and `finalize()` flushes whatever is still buffered. For a string you already have, call them one after the other.

### Streaming LLM responses

```python
from markrender import MarkdownRenderer
from openai import OpenAI

client = OpenAI()
renderer = MarkdownRenderer(theme="github-dark")

stream = client.chat.completions.create(
    model="gpt-4o",
    messages=[{"role": "user", "content": "Explain quantum computing"}],
    stream=True,
)

for chunk in stream:
    text = chunk.choices[0].delta.content
    if text:
        renderer.render(text)

renderer.finalize()
```

The renderer keeps partial lines and open blocks in an internal buffer, so chunks can split anywhere: mid-word, mid-table, or in the middle of a code fence. Feed every chunk and call `finalize()` once when the stream ends.

### Dim mode

`render()` takes a `dim_mode` argument, which draws that chunk as plain muted gray. Formatting colors, bold, and syntax highlighting are dropped so the whole block reads like thinking text instead of competing with the answer:

```python
renderer.render("Let me think about this...", dim_mode=True)
renderer.render("Here is the answer.", dim_mode=False)
```

Dim mode applies per call, so you can turn it on and off while streaming.

### Custom output

By default output goes to stdout. Pass any text stream with `output`:

```python
from markrender import MarkdownRenderer

with open("rendered.txt", "w", encoding="utf-8") as log:
    renderer = MarkdownRenderer(output=log, force_color=True)
    renderer.render("# Saved to a file\n")
    renderer.finalize()
```

Color detection still looks at stdout, so set `force_color=True` if you want ANSI colors in the file.

### Constructor options

| Parameter | Default | Description |
|-----------|---------|-------------|
| `theme` | `"github-dark"` | Theme name |
| `code_background` | `False` | Draw a background behind code blocks |
| `line_numbers` | `True` | Show line numbers in code blocks |
| `inline_code_color` | theme default | ANSI color code for inline code |
| `width` | auto-detect | Wrap width in characters |
| `force_color` | `False` | Emit color even when the output is not a TTY |
| `stream_code` | `True` | Render code lines as they arrive |
| `output` | `sys.stdout` | Stream to write to |
| `use_config` | `True` | Load a config file if one is found |
| `config` | `None` | Pass a `RendererConfig` directly |

Custom inline code color uses the `rgb` helper:

```python
from markrender import MarkdownRenderer
from markrender.colors import rgb

renderer = MarkdownRenderer(
    theme="monokai",
    inline_code_color=rgb(255, 100, 200),
    width=100,
)
```

## Configuration

MarkRender reads a TOML config file if one exists. It checks these locations in order and uses the first match:

1. `.markrender.toml` in the current directory
2. `~/.markrender/config.toml`
3. `~/.config/markrender/config.toml`

Example `.markrender.toml`:

```toml
[theme]
name = "dracula"

[rendering]
code_background = true
line_numbers = false

[output]
width = 100
force_color = false

[features]
stream_code = false
```

Values are applied in this order, from highest to lowest priority:

1. Arguments passed to `MarkdownRenderer(...)`
2. The config file
3. Built-in defaults

Only non-`None` arguments override the config, so `MarkdownRenderer()` picks up your file settings. Pass `use_config=False` to ignore config files entirely.

## Themes

| Theme | Notes |
|-------|-------|
| `github-dark` | GitHub's dark theme (default) |
| `monokai` | Classic Monokai palette |
| `dracula` | Dracula palette |
| `nord` | Nord palette |
| `one-dark` | Atom One Dark |
| `solarized-dark` | Solarized Dark |
| `solarized-light` | Solarized Light |

```python
renderer = MarkdownRenderer(theme="dracula")
```

See the names from the CLI with `markrender --list-themes`, or render a sample in each theme with `markrender --preview-themes`.

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

## Changelog

Release notes come from conventional commit messages, so the history stays in
one place. See [CHANGELOG.md](CHANGELOG.md) for what changed in each version.

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

To eyeball every supported markdown feature at once, render the sample fixture:

```bash
markrender tests/fixtures/sample.md
```

### Releasing

The package version is derived from git tags by `setuptools_scm`, so there is
no version number to edit by hand.

1. Open **Actions → Publish → Run workflow**.
2. Choose `auto` (recommended) or an explicit `patch`, `minor`, or `major` bump.
3. The workflow runs the tests, creates the next `vX.Y.Z` tag, builds the
   sdist and wheel, publishes to PyPI, and creates a GitHub release.
4. Release notes are generated from the commits since the last tag, and the
   same entry is added to [CHANGELOG.md](CHANGELOG.md) on `main`.

With `auto`, commit messages since the last tag decide the bump:

- `feat!:` or a `BREAKING CHANGE:` footer → major
- `feat:` → minor
- `fix:`, `perf:`, `refactor:`, or `revert:` → patch
- `docs:`, `test:`, `chore:`, `ci:`, `build:`, and `style:` don't trigger a
  release on their own

Write commit subjects in the `type(scope): summary` form so the changelog and
version bump stay accurate.

Publishing uses PyPI Trusted Publishing (OIDC), so no API token is stored in
the repository. Configure it once:

- **PyPI:** project `markrender` → Publishing → add a trusted publisher with
  owner `Praneeth-Gandodi`, repository `markrender`, workflow `publish.yml`,
  environment `pypi`.
- **GitHub:** Settings → Environments → create an environment named `pypi`.

The repository default workflow permission can stay read-only; the workflow
requests `contents: write` only for the jobs that create the tag and release.

You can also publish an existing tag directly:

```bash
git tag v1.1.0
git push origin v1.1.0
```

To publish automatically after every merge to `main`, uncomment the `branches:
[main]` trigger in `.github/workflows/publish.yml`.

## License

MIT License - see [LICENSE](LICENSE) file for details.
