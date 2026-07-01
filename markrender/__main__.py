"""
Command-line entry point for MarkRender
Reads markdown from stdin or a file and renders it to the terminal
"""

import sys
import argparse
from pathlib import Path

from .renderer import MarkdownRenderer
from .themes import list_themes


def preview_themes():
    """Preview all available themes"""
    line = '=' * 60
    sep = '-' * 60

    print(line)
    print("MarkRender Theme Preview")
    print(line)
    print()

    sample_markdown = """
## Sample Heading 2
This is a sample text with **bold**, *italic*, and `inline code`.

```python
def hello():
    print("Hello, World!")
```

- List item 1
- List item 2

> A blockquote example

| Col1 | Col2 |
|------|------|
| A    | B    |
"""

    for theme_name in list_themes():
        print(f"\n{sep}")
        print(f"Theme: {theme_name}")
        print(sep)

        renderer = MarkdownRenderer(
            theme=theme_name,
            line_numbers=False,
            code_background=False,
            force_color=True
        )
        renderer.render(sample_markdown)
        renderer.finalize()
        print()

    print("\n" + line)
    print(f"Total themes: {len(list_themes())}")
    print(line)


def main():
    parser = argparse.ArgumentParser(
        description='MarkRender - Professional Terminal Markdown Renderer',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Examples:
  markrender README.md
  markrender --theme dracula file.md
  cat file.md | markrender
  markrender --list-themes
  markrender --preview-themes"""
    )

    parser.add_argument(
        'file',
        nargs='?',
        default=None,
        help='Markdown file to render (reads from stdin if not provided)'
    )

    parser.add_argument(
        '--theme',
        default='github-dark',
        help=f'Color theme (default: github-dark). Available: {", ".join(list_themes())}'
    )

    parser.add_argument(
        '--no-line-numbers',
        action='store_true',
        help='Hide line numbers in code blocks'
    )

    parser.add_argument(
        '--code-background',
        action='store_true',
        help='Show background in code blocks'
    )

    parser.add_argument(
        '--width',
        type=int,
        default=None,
        help='Terminal width (default: auto-detect)'
    )

    parser.add_argument(
        '--no-stream-code',
        action='store_true',
        help='Render code blocks all at once instead of line by line'
    )

    parser.add_argument(
        '--force-color',
        action='store_true',
        help='Force color output even if terminal does not support it'
    )

    parser.add_argument(
        '--list-themes',
        action='store_true',
        help='List available themes and exit'
    )

    parser.add_argument(
        '--preview-themes',
        action='store_true',
        help='Preview all available themes with sample content and exit'
    )

    parser.add_argument(
        '-v', '--version',
        action='version',
        version='markrender 1.0.0'
    )

    args = parser.parse_args()

    if args.list_themes:
        print("Available themes:")
        for theme in list_themes():
            print(f"  {theme}")
        return

    if args.preview_themes:
        preview_themes()
        return

    try:
        if args.file:
            file_path = Path(args.file)
            if not file_path.exists():
                print(f"Error: File '{args.file}' not found", file=sys.stderr)
                sys.exit(1)
            try:
                content = file_path.read_text(encoding='utf-8')
            except UnicodeDecodeError:
                try:
                    content = file_path.read_text(encoding='latin-1')
                    print(f"Warning: File {args.file} is not UTF-8 encoded. Using latin-1 fallback.", file=sys.stderr)
                except (UnicodeDecodeError, OSError, IOError):
                    print(f"Error: Could not read file {args.file}. It might be a binary file.", file=sys.stderr)
                    sys.exit(1)
        else:
            if sys.stdin.isatty():
                print("Error: No input file specified and no data piped to stdin.", file=sys.stderr)
                print("Usage: markrender [file]", file=sys.stderr)
                print("   or: cat file.md | markrender", file=sys.stderr)
                sys.exit(1)
            try:
                content = sys.stdin.read()
            except UnicodeDecodeError:
                try:
                    if hasattr(sys.stdin, 'reconfigure'):
                        sys.stdin.reconfigure(encoding='latin-1', errors='replace')
                        content = sys.stdin.read()
                    else:
                        content = sys.stdin.buffer.read().decode('latin-1', errors='replace')
                except Exception:
                    print("Error: Could not read from stdin. It might be a binary stream.", file=sys.stderr)
                    sys.exit(1)

        if not content:
            return

        renderer = MarkdownRenderer(
            theme=args.theme,
            code_background=args.code_background,
            line_numbers=not args.no_line_numbers,
            width=args.width,
            stream_code=not args.no_stream_code,
            force_color=args.force_color,
        )

        renderer.render(content)
        renderer.finalize()

    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nInterrupted", file=sys.stderr)
        sys.exit(130)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
