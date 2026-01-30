"""
Output formatters for markdown elements
Handles rendering of headings, code, tables, lists, and more
"""

import re
from pygments import highlight
from pygments.lexers import get_lexer_by_name, TextLexer
from pygments.formatters import Terminal256Formatter
from pygments.util import ClassNotFound
try:
    import emoji as emoji_lib
except ImportError:
    emoji_lib = None

try:
    from rich.table import Table
    from rich.console import Console
    from rich.text import Text
    from io import StringIO
    rich_available = True
except ImportError:
    rich_available = False

from .colors import colorize, Colors, get_terminal_width


class MarkdownFormatter:
    """Formats markdown elements for terminal output"""
    
    def __init__(self, theme_config, inline_code_color=None, code_background=False, width=None):
        """
        Initialize formatter
        
        Args:
            theme_config: Theme configuration dict
            inline_code_color: Custom color for inline code (default from theme)
            code_background: Whether to show background in code blocks
            width: Terminal width (auto-detect if None)
        """
        self.theme = theme_config
        self.inline_code_color = inline_code_color or theme_config['inline_code']
        self.code_background = code_background
        self.width = width or get_terminal_width()
    
    def format_heading(self, level, text):
        """
        Format heading (H1-H6) with left justification and color
        
        Args:
            level: Heading level (1-6)
            text: Heading text
        
        Returns:
            Formatted heading string
        """
        level = max(1, min(6, level))  # Clamp to 1-6
        color = self.theme['heading_colors'].get(level, Colors.WHITE)
        
        # Different symbols for different heading levels
        if level == 1:
            text = colorize(f'{text}', color + Colors.BOLD)
            return f'\n{text}\n'
        elif level == 2:
            text = colorize(f'{text}', color + Colors.BOLD)
            return f'\n{text}\n'
        else:
            text = colorize(f'{text}', color)
            return f'\n{text}\n'
    
    def format_code_block(self, code, language='', line_numbers=True):
        """
        Format code block with syntax highlighting
        
        Args:
            code: Code content
            language: Programming language for syntax highlighting
            line_numbers: Whether to show line numbers
        
        Returns:
            Formatted code block string
        """
        # Get lexer
        try:
            if language:
                lexer = get_lexer_by_name(language, stripall=True)
            else:
                lexer = TextLexer()
        except ClassNotFound:
            lexer = TextLexer()
        
        # Format code with pygments
        formatter = Terminal256Formatter(style=self.theme.get('pygments_style', 'monokai'))
        highlighted = highlight(code, lexer, formatter).rstrip()
        
        # Add line numbers if requested
        if line_numbers:
            lines = highlighted.split('\n')
            max_line_num = len(lines)
            num_width = len(str(max_line_num))
            
            formatted_lines = []
            for i, line in enumerate(lines, 1):
                line_num = colorize(f'{i:>{num_width}}', Colors.BRIGHT_BLACK)
                # Add background if requested
                if self.code_background:
                    formatted_lines.append(f'{Colors.BG_BRIGHT_BLACK} {line_num} {Colors.RESET} {line}')
                else:
                    formatted_lines.append(f' {line_num}  {line}')
            
            result = '\n'.join(formatted_lines)
        else:
            result = highlighted
        
        # Add spacing
        return f'\n{result}\n'
    
    def format_inline_code(self, text):
        """
        Format inline code with custom color
        
        Args:
            text: Code text
        
        Returns:
            Formatted inline code string
        """
        return colorize(f'{text}', self.inline_code_color)
    
    def format_table(self, rows):
        """
        Format markdown table with borders using rich
        
        Args:
            rows: List of lists representing table rows
        
        Returns:
            Formatted table string
        """
        if not rich_available or not rows:
            return ''

        header = rows[0]
        # The separator is the second row, which we can ignore
        data_rows = rows[2:]

        table = Table(show_header=True, header_style="bold magenta")

        for col in header:
            table.add_column(col)

        for row in data_rows:
            table.add_row(*[str(cell) for cell in row])

        console = Console(file=StringIO(), width=self.width, force_terminal=True)
        console.print(table)
        output = console.file.getvalue()
        
        # Rich adds a newline, we might not want that if we add more
        return '\n' + output.rstrip() + '\n'

    
    def format_list_item(self, text, ordered=False, number=1, indent_level=0):
        """
        Format list item (bullet or numbered)
        
        Args:
            text: List item text
            ordered: Whether this is an ordered list
            number: Item number (for ordered lists)
            indent_level: Indentation level
        
        Returns:
            Formatted list item string
        """
        indent = '  ' * indent_level
        if ordered:
            marker = colorize(f'{number}.', Colors.BRIGHT_BLUE)
        else:
            marker = colorize('•', Colors.BRIGHT_BLUE)
        
        return f'{indent}{marker} {text}'
    
    def format_checkbox(self, checked, text):
        """
        Format checkbox (task list item)
        
        Args:
            checked: Whether checkbox is checked
            text: Checkbox text
        
        Returns:
            Formatted checkbox string
        """
        if checked:
            box = colorize('✅', self.theme['checkbox_checked'])
        else:
            box = colorize('⬜', self.theme['checkbox_unchecked'])
        
        return f'{box}  {text}'
    
    def format_blockquote(self, text, nesting_level=0):
        """
        Format blockquote with border

        Args:
            text: Blockquote text
            nesting_level: The nesting level of the blockquote

        Returns:
            Formatted blockquote string
        """
        stripped_text = text.strip()
        if stripped_text.startswith('**Note:**'):
            note_color = self.theme.get('note_color', Colors.YELLOW)
            # We want to format the "**Note:**" part bold, and the rest normal
            parts = stripped_text.split('**Note:**', 1)
            if len(parts) > 1:
                note_text = colorize('Note:', Colors.BOLD)
                rest_of_text = parts[1]
                return colorize(f'{note_text}{rest_of_text}', note_color)
            else:
                return colorize(stripped_text, note_color)
        else:
            border_char = colorize('│', self.theme['blockquote_border'])
            indentation = '  ' * nesting_level
            lines = text.split('\n')
            formatted = [f'{indentation}{border_char} {line}' for line in lines]
            return '\n'.join(formatted)
    
    def format_link(self, text, url):
        """
        Format link with OSC 8 ANSI escape sequence for clickable links
        
        Args:
            text: Link text
            url: Link URL
        
        Returns:
            Formatted link string
        """
        link_color = self.theme['link']
        
        # OSC 8 hyperlink format: \x1b]8;;URL\x1b\\TEXT\x1b]8;;\x1b\\
        osc_start = f'\x1b]8;;{url}\x1b\\'
        osc_end = '\x1b]8;;\x1b\\'
        
        # Colorize and underline the link text
        colored_text = colorize(text, link_color + Colors.UNDERLINE)
        
        return f'{osc_start}{colored_text}{osc_end}'
    
    def format_hr(self):
        """
        Format horizontal rule
        
        Returns:
            Formatted horizontal rule string
        """
        width = min(self.width, 80)
        line = '─' * width
        return '\n' + colorize(line, self.theme['hr']) + '\n'
    
    def format_emoji(self, emoji_code):
        """
        Convert emoji code to emoji character
        
        Args:
            emoji_code: Emoji code (e.g., 'smile', 'fire')
        
        Returns:
            Emoji character or original code if not found
        """
        if emoji_lib:
            try:
                return emoji_lib.emojize(f':{emoji_code}:', language='alias')
            except Exception:
                pass
        return f':{emoji_code}:'
    
    def format_bold(self, text):
        """Format bold text"""
        return colorize(text, Colors.BOLD)
    
    def format_italic(self, text):
        """Format italic text"""
        return colorize(text, Colors.ITALIC)
    
    def format_strikethrough(self, text):
        """Format strikethrough text"""
        return colorize(text, Colors.DIM)
