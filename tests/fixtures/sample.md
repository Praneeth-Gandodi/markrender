# MarkRender Test Suite

Welcome to the comprehensive markrender test file. This file exercises every
markdown feature the renderer supports so you can visually verify everything
works correctly.

---

## 1. Headings

### 1.1 All Six Levels

# Heading Level 1
## Heading Level 2
### Heading Level 3
#### Heading Level 4
##### Heading Level 5
###### Heading Level 6

### 1.2 Headings with Inline Formatting

# **Bold Heading**
## *Italic Heading*
### `Code Heading`
#### ~~Strikethrough Heading~~
##### [Link Heading](https://example.com)
###### Mixed **Bold** and *Italic*

### 1.3 Headings with Emoji

# :rocket: Getting Started
## :star: Key Features
### :wrench: Configuration
#### :test_tube: Testing
##### :package: Deployment
###### :book: Documentation

---

## 2. Text Formatting

### 2.1 Bold and Italic

This is **bold text** and this is *italic text*.
This is ***bold and italic*** together.
This is **bold with *nested italic***.
This is *italic with **nested bold***.

### 2.2 Strikethrough

This is ~~deleted text~~.
This is ~~strikethrough with **bold** inside~~.
This is **bold with ~~strikethrough~~ inside**.

### 2.3 Inline Code

Use the `print()` function to output text.
The `os.path.join()` function handles paths.
Nested: `` `code` inside backticks `` doesn't work but `**bold**` inside code should be literal.

### 2.4 Combined Formatting

**Bold** with *italic* and `code` and ~~strike~~ all in one line.
*Italic with `inline code` inside* and **bold too**.
`Code with *italic* markup` should show the asterisks literally.

### 2.5 Links

Visit [GitHub](https://github.com) for hosting.
Read the [documentation](https://example.com/docs) for details.
Here's a [link with **bold text**](https://example.com).
And a [link with `code`](https://example.com/code).

### 2.6 Images

![MarkRender Logo](https://example.com/logo.png)
![Icon](icon.png)
![Diagram with **bold** alt](diagram.png)

### 2.7 Emoji

Hello :wave: and welcome :tada:
Let's go :rocket: to the moon :moon:
I :heart: markdown :sparkles:
:fire: :fire: :fire: Hot stuff!
Check the box :white_check_mark:
Warning :warning: :warning: :warning:
:+1: This is great!
:smile: :laughing: :joy: :sunglasses:

### 2.8 Special Characters

HTML entities: &amp; &lt; &gt; &quot; &#39;
Mathematical: x^2 + y^2 = z^2, H2O, E=mc^2
Unicode: © ® ™ € £ ¥ ° ± × ÷ ∞ µ π ∆ ← ↑ → ↓

---

## 3. Code Blocks

### 3.1 Python

```python
def fibonacci(n):
    """Calculate the nth Fibonacci number."""
    if n <= 1:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)


def main():
    for i in range(10):
        print(f"fib({i}) = {fibonacci(i)}")


if __name__ == "__main__":
    main()
```

### 3.2 JavaScript

```javascript
function fibonacci(n) {
  if (n <= 1) return n;
  return fibonacci(n - 1) + fibonacci(n - 2);
}

for (let i = 0; i < 10; i++) {
  console.log(`fib(${i}) = ${fibonacci(i)}`);
}
```

### 3.3 HTML

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>MarkRender Demo</title>
  <style>
    body { font-family: sans-serif; }
    .highlight { color: blue; }
  </style>
</head>
<body>
  <h1>Hello, World!</h1>
  <p>This is a <strong>test</strong> page.</p>
</body>
</html>
```

### 3.4 CSS

```css
.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
}

.card {
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  padding: 1.5rem;
}

.card:hover {
  transform: translateY(-2px);
  transition: transform 0.2s ease;
}
```

### 3.5 SQL

```sql
SELECT
  u.name,
  COUNT(o.id) AS order_count,
  SUM(o.total) AS total_spent
FROM users u
LEFT JOIN orders o ON u.id = o.user_id
WHERE u.active = true
  AND o.created_at >= '2024-01-01'
GROUP BY u.id, u.name
HAVING COUNT(o.id) > 5
ORDER BY total_spent DESC
LIMIT 10;
```

### 3.6 Rust

```rust
use std::collections::HashMap;

#[derive(Debug)]
struct Config {
    host: String,
    port: u16,
    debug: bool,
}

impl Config {
    fn new(host: &str, port: u16) -> Self {
        Config {
            host: host.to_string(),
            port,
            debug: false,
        }
    }

    fn display(&self) -> String {
        format!("{}:{} (debug: {})", self.host, self.port, self.debug)
    }
}
```

### 3.7 Empty Code Block

```
```

### 3.8 Consecutive Code Blocks

```python
print("First block")
```

```python
print("Second block")
```

```python
print("Third block")
```

### 3.9 Code Block with No Language

```
This is a plain text code block
with no syntax highlighting
just raw monospaced text
```

---

## 4. Tables

### 4.1 Simple Table

| Name | Age | City |
|------|-----|------|
| Alice | 30 | New York |
| Bob | 25 | Los Angeles |
| Charlie | 35 | Chicago |
| Diana | 28 | Houston |

### 4.2 Table with Inline Formatting

| Feature | Status | Notes |
|---------|--------|-------|
| **Bold** | `done` | *Works* |
| *Italic* | ~~wip~~ | **Nice** |
| `Code` | done | ~~strike~~ |

### 4.3 Table with Inconsistent Columns

| Header A | Header B | Header C |
|----------|----------|----------|
| Short | Long value here |
| A | B | C |
| Single |
| | Middle | |
| | | Last |

### 4.4 Wide Table

| Language | Type | Paradigm | Typing | First Release | Latest Version |
|----------|------|----------|-------|---------------|----------------|
| Python | Interpreted | Multi | Dynamic | 1991 | 3.12 |
| Rust | Compiled | Multi | Static | 2010 | 1.75 |
| Go | Compiled | Concurrent | Static | 2009 | 1.21 |
| TypeScript | Transpiled | Object | Static | 2012 | 5.3 |
| Elixir | Interpreted | Functional | Dynamic | 2011 | 1.15 |

### 4.5 Table with Links

| Resource | URL | Description |
|----------|-----|-------------|
| GitHub | [github.com](https://github.com) | Code hosting |
| PyPI | [pypi.org](https://pypi.org) | Python packages |
| npm | [npmjs.com](https://www.npmjs.com) | Node packages |

---

## 5. Lists

### 5.1 Unordered List

- Item one
- Item two
- Item three
- Item four
- Item five

### 5.2 Ordered List

1. First step
2. Second step
3. Third step
4. Fourth step
5. Fifth step

### 5.3 Nested Unordered List

- Level 1 item
  - Level 2 item
    - Level 3 item
      - Level 4 item
  - Another level 2
- Back to level 1
  - Level 2 again
    - Level 3 again

### 5.4 Nested Ordered List

1. Step one
   1. Sub-step A
      1. Sub-sub-step i
      2. Sub-sub-step ii
   2. Sub-step B
2. Step two
   1. Sub-step C
3. Step three

### 5.5 Mixed Nested List

- Category A
  1. Item A1
  2. Item A2
    - Sub-item A2a
    - Sub-item A2b
- Category B
  - Item B1
  - Item B2
    1. Ordered B2a
    2. Ordered B2b

### 5.6 List Items with Formatting

- **Bold list item**
- *Italic list item*
- `Code list item`
- [Link list item](https://example.com)
- ~~Strikethrough list item~~
- Mixed **bold** and *italic* and `code`
- :rocket: Emoji in list item

---

## 6. Checkboxes

### 6.1 Simple Task List

- [x] Completed task
- [ ] Pending task
- [x] Another done task
- [ ] Yet to do
- [x] Finished item
- [ ] Not started

### 6.2 Checkboxes with Formatting

- [x] **Bold task** completed
- [ ] *Italic task* pending
- [ ] `Code review` not done
- [x] [Link task](https://example.com) done
- [ ] ~~Strikethrough task~~ wait, still open

### 6.3 Nested Checkboxes

- [x] Project setup
  - [x] Install dependencies
  - [x] Configure build
  - [ ] Set up CI
- [ ] Development
  - [x] Core feature
  - [ ] Tests
    - [x] Unit tests
    - [ ] Integration tests
  - [ ] Documentation
- [ ] Deployment
  - [ ] Staging
  - [ ] Production

---

## 7. Blockquotes

### 7.1 Single Line

> This is a simple blockquote.

### 7.2 Multi-line

> This is a blockquote
> that spans multiple
> lines of text.

### 7.3 Blockquote with Formatting

> **Important:** This is a critical note.
> *Please read carefully* before proceeding.
> Use `config.setup()` to initialize.
> See the [docs](https://example.com) for details.

### 7.4 Nested Blockquotes

> Level 1
>
> > Level 2
> >
> > > Level 3

### 7.5 Blockquote with Code

> Here's an example:
>
> ```python
> def hello():
>     print("Hello from blockquote!")
> ```
>
> And that's it.

### 7.6 Blockquote with List

> Things to remember:
> - Always validate input
> - Handle errors gracefully
> - Write tests first
>
> 1. Plan
> 2. Code
> 3. Test
> 4. Deploy

---

## 8. Horizontal Rules

---

Above is a standard horizontal rule.

***

Above is made with asterisks.

___

Above is made with underscores.

---

## 9. Mixed Content

### 9.1 Paragraph with Everything

Welcome to **MarkRender**, a *professional* terminal markdown renderer for
streaming LLM responses. It supports `inline code`, ~~strikethrough~~,
[links](https://github.com), :emoji:, and more! Here's an image
![icon](icon.png) inline in text.

### 9.2 Section with All Elements

# Big Title

Some introductory text here.

## Code Example

```python
def greet(name):
    return f"Hello, {name}!"
```

### Key Points

- Point one with **bold**
- Point two with *italic*
- Point three with `code`

| Property | Value |
|----------|-------|
| Name | MarkRender |
| Version | 1.0.0 |

> Final thought: This is a complete example.

---

## 10. Edge Cases

### 10.1 Very Long Single Line

This is a very long line of text that should wrap properly in the terminal display. It contains **bold text**, *italic text*, `inline code`, a [link](https://example.com/with/a/very/long/path/that/goes/on/and/on), and also some :emoji: :rocket: :fire: :sparkles: for good measure. The goal is to test that the renderer handles long lines without breaking or truncating content incorrectly. Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.

### 10.2 Empty Lines Between Elements

Above this line there should be proper spacing.


Below this line there should also be proper spacing.



And even more spacing above this line.

### 10.3 Consecutive Horizontal Rules

---

---



---

### 10.4 Consecutive Headings

# Heading A
## Heading B
### Heading C
### Heading D
## Heading E
# Heading F

### 10.5 Special Characters in Code

```python
special_chars = "!@#$%^&*()_+-=[]{}|;':\",./<>?~`"
escape_sequences = "\n\t\r\\\b\f\a"
unicode_text = "ñóêüçàèìòù€£¥§¿¡⇒⇔∈∉⊂⊃∪∩"
```

---

## 11. All Features Combined

# :tada: MarkRender Complete Test :tada:

This final section demonstrates **everything** working together in one flow.

## Code Sample

```python
import sys
from markrender import MarkdownRenderer

def main():
    """Demo all features."""
    renderer = MarkdownRenderer(
        theme='github-dark',
        line_numbers=True,
        code_background=False
    )

    renderer.render("# Hello :wave:\n")
    renderer.render("**Bold**, *italic*, `code`\n")
    renderer.finalize()
```

## Feature Table

| Feature | Status | Priority | Notes |
|---------|--------|----------|-------|
| **Headings** | :white_check_mark: | High | All 6 levels |
| *Code Blocks* | :white_check_mark: | High | + highlighting |
| `Tables` | :white_check_mark: | High | With borders |
| Links | :white_check_mark: | Medium | Styled URLs |
| :heart: Emoji | :white_check_mark: | Medium | Library support |
| ~~Edge Cases~~ | :white_check_mark: | Low | All covered |

## Task Status

- [x] Test headings
- [x] Test code blocks
- [x] Test tables
- [x] Test formatting
- [x] Test lists
- [ ] ~~Add more tests~~ All done!

## GFM Alerts

> [!NOTE]
> This is a standard **note** for general information.

> [!TIP]
> Here's a *helpful tip* to make things easier.

> [!IMPORTANT]
> This is **critical** information you shouldn't miss.

> [!WARNING]
> Proceed with *caution* — this could cause issues.

> [!CAUTION]
> This could result in **data loss** or errors.

---

## Final Quote

> MarkRender makes terminal markdown **beautiful**.
> No flickering, no lag, just *clean* output.
> :sparkles: :tada: :rocket:

---

Thank you for testing MarkRender!

This file was automatically generated for testing purposes.
