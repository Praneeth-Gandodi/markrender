#!/usr/bin/env python3
"""
Command-line interface for MarkRender
"""

import argparse
import sys
import os
from pathlib import Path

from .renderer import MarkdownRenderer
from .themes import list_themes, get_theme
from .colors import Colors


def preview_themes():
    """Preview all available themes"""
    print("=" * 60)
    print("MarkRender Theme Preview")
    print("=" * 60)
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
        print(f"\n{'─' * 60}")
        print(f"Theme: {theme_name}")
        print('─' * 60)
        
        renderer = MarkdownRenderer(
            theme=theme_name,
            line_numbers=False,
            code_background=False,
            force_color=True
        )
        renderer.render(sample_markdown)
        renderer.finalize()
        print()
    
    print("\n" + "=" * 60)
    print(f"Total themes: {len(list_themes())}")
    print("=" * 60)


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        prog='markrender',
        description='Render Markdown in the terminal with beautiful formatting',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  markrender README.md
  markrender --theme dracula file.md
  cat file.md | markrender
  markrender --list-themes
  markrender --preview-themes
        """
    )

    parser.add_argument(
        'file',
        nargs='?',
        default=None,
        help='Markdown file to render (default: stdin)'
    )

    parser.add_argument(
        '-t', '--theme',
        choices=list_themes(),
        default='github-dark',
        help='Syntax highlighting theme (default: github-dark)'
    )

    parser.add_argument(
        '--no-line-numbers',
        action='store_true',
        help='Disable line numbers in code blocks'
    )

    parser.add_argument(
        '--code-background',
        action='store_true',
        help='Enable background color in code blocks'
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
        version='%(prog)s 1.0.7'
    )

    args = parser.parse_args()

    # Handle --list-themes
    if args.list_themes:
        print("Available themes:")
        for theme in list_themes():
            print(f"  - {theme}")
        return 0

    # Handle --preview-themes
    if args.preview_themes:
        preview_themes()
        return 0

    try:
        # Create renderer with specified options
        renderer = MarkdownRenderer(
            theme=args.theme,
            code_background=args.code_background,
            line_numbers=not args.no_line_numbers,
            width=args.width,
            force_color=args.force_color,
            stream_code=not args.no_stream_code
        )

        # Read input content
        if args.file is None:
            content = sys.stdin.read()
        else:
            file_path = Path(args.file)
            if not file_path.exists():
                print(f"Error: File not found: {file_path}", file=sys.stderr)
                return 1
            
            try:
                # Try reading as UTF-8
                content = file_path.read_text(encoding='utf-8')
            except UnicodeDecodeError:
                # Try reading with latin-1 as fallback if it's not binary
                try:
                    content = file_path.read_text(encoding='latin-1')
                    print(f"Warning: File {file_path} is not UTF-8 encoded. Using latin-1 fallback.", file=sys.stderr)
                except Exception:
                    print(f"Error: Could not read file {file_path}. It might be a binary file.", file=sys.stderr)
                    return 1

        renderer.render(content)
        renderer.finalize()

        return 0

    except FileNotFoundError as e:
        print(f"Error: File not found: {e}", file=sys.stderr)
        return 1
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print("\nInterrupted", file=sys.stderr)
        return 130
    except Exception as e:
        import traceback
        # print(traceback.format_exc()) # For debugging
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
