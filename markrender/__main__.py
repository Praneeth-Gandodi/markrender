"""
Command-line entry point for MarkRender
Reads markdown from stdin or a file and renders it to the terminal
"""

import sys
import argparse
from .renderer import MarkdownRenderer
from .themes import list_themes


def main():
    parser = argparse.ArgumentParser(
        description='MarkRender - Professional Terminal Markdown Renderer'
    )
    parser.add_argument(
        'file',
        nargs='?',
        help='Markdown file to render (reads from stdin if not provided)'
    )
    parser.add_argument(
        '--theme',
        default='github-dark',
        help=f'Color theme (default: github-dark). Available: {", ".join(list_themes())}'
    )
    parser.add_argument(
        '--list-themes',
        action='store_true',
        help='List available themes and exit'
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

    args = parser.parse_args()

    if args.list_themes:
        print("Available themes:")
        for theme in list_themes():
            print(f"  {theme}")
        return

    if args.file:
        try:
            with open(args.file, 'r', encoding='utf-8') as f:
                content = f.read()
        except FileNotFoundError:
            print(f"Error: File '{args.file}' not found", file=sys.stderr)
            sys.exit(1)
        except IOError as e:
            print(f"Error reading file: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        content = sys.stdin.read()

    if not content:
        return

    renderer = MarkdownRenderer(
        theme=args.theme,
        code_background=args.code_background,
        line_numbers=not args.no_line_numbers
    )

    renderer.render(content)
    renderer.finalize()


if __name__ == '__main__':
    main()
