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
    
    def __init__(self, theme_config, inline_code_color=None, code_background=False, width=None, force_color=False):
        """
        Initialize formatter
        
        Args:
            theme_config: Theme configuration dict
            inline_code_color: Custom color for inline code (default from theme)
            code_background: Whether to show background in code blocks
            width: Terminal width (auto-detect if None)
            force_color: Force color output (bypasses terminal capability check)
        """
        self.theme = theme_config
        self.inline_code_color = inline_code_color or theme_config['inline_code']
        self.code_background = code_background
        self.width = width or get_terminal_width()
        self.force_color = force_color
    
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
            text = colorize(f'{text}', color + Colors.BOLD, force_color=self.force_color)
            return f'\n{text}\n'
        elif level == 2:
            text = colorize(f'{text}', color + Colors.BOLD, force_color=self.force_color)
            return f'\n{text}\n'
        else:
            text = colorize(f'{text}', color, force_color=self.force_color)
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
                line_num = colorize(f'{i:>{num_width}}', Colors.BRIGHT_BLACK, force_color=self.force_color)
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
        return colorize(f'{text}', self.inline_code_color, force_color=self.force_color)
    
    def format_table(self, header, data_rows):
        """
        Format markdown table with borders using rich
        
        Args:
            header: List of strings for table header
            data_rows: List of lists of strings representing table data rows
        
        Returns:
            Formatted table string
        """
        if not rich_available or not header:
            return ''

        # Initialize rich Table
        table = Table(show_header=True, header_style="bold magenta", expand=True)

        # Add columns
        for col_title in header: # Allow headers to wrap
            table.add_column(col_title)

        # Add data rows
        for row_data in data_rows:
            table.add_row(*[str(cell) for cell in row_data])

        # Render table to string
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
            marker = colorize(f'{number}.', Colors.BRIGHT_BLUE, force_color=self.force_color)
        else:
            marker = colorize('•', Colors.BRIGHT_BLUE, force_color=self.force_color)
        
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
            box = colorize('✅', self.theme['checkbox_checked'], force_color=self.force_color)
        else:
            box = colorize('⬜', self.theme['checkbox_unchecked'], force_color=self.force_color)
        
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
        stripped_text_first_line = text.strip().split('\n')[0] # Only check first line for callout
        callout_types = {
            "NOTE": self.theme.get('note_color', Colors.CYAN),
            "TIP": self.theme.get('tip_color', Colors.GREEN),
            "IMPORTANT": self.theme.get('important_color', Colors.MAGENTA),
            "WARNING": self.theme.get('warning_color', Colors.YELLOW),
            "CAUTION": self.theme.get('caution_color', Colors.RED),
            "ATTENTION": self.theme.get('attention_color', Colors.RED), # Adding common callout
        }
        
        # Regex to detect `[!TYPE]` at the beginning of the text
        callout_match = re.match(r'^\[!(NOTE|TIP|IMPORTANT|WARNING|CAUTION|ATTENTION)\]\s*(.*)', stripped_text_first_line, re.IGNORECASE)

        if callout_match:
            callout_type = callout_match.group(1).upper()
            message_first_line = callout_match.group(2).strip()
            
            # Reconstruct the full message, removing the matched callout syntax from the first line
            full_message = message_first_line
            if '\n' in text:
                # Append remaining lines of the blockquote to the message
                full_message += '\n' + '\n'.join(text.strip().split('\n')[1:])
            
            type_color = callout_types.get(callout_type, Colors.WHITE)
            
            formatted_type = colorize(f'{callout_type}:', Colors.BOLD + type_color, force_color=self.force_color)
            
            # Format each line of the message separately to apply color
            formatted_message_lines = [colorize(line, type_color, force_color=self.force_color) for line in full_message.split('\n')]
            
            # Reassemble without the blockquote border, just indentation
            indentation = '  ' * nesting_level
            # The first line has the type and the message. Subsequent lines are just message.
            lines = [f'{indentation} {formatted_type} {formatted_message_lines[0]}'] + \
                    [f'{indentation}   {line}' for line in formatted_message_lines[1:]] # Indent subsequent lines
            return '\n'.join(lines)

        # Fallback to generic blockquote formatting
        border_char = colorize('│', self.theme['blockquote_border'], force_color=self.force_color)
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
        colored_text = colorize(text, link_color + Colors.UNDERLINE, force_color=self.force_color)
        
        return f'{osc_start}{colored_text}{osc_end}'
    
    def format_hr(self):
        """
        Format horizontal rule
        
        Returns:
            Formatted horizontal rule string
        """
        width = min(self.width, 80)
        line = '─' * width
        return '\n' + colorize(line, self.theme['hr'], force_color=self.force_color) + '\n'
    
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
                # Emojize does not take force_color parameter, it returns raw emoji
                return emoji_lib.emojize(f':{emoji_code}:', language='alias')
            except Exception:
                pass
        return f':{emoji_code}:'
    
    def format_bold(self, text):
        """Format bold text"""
        return colorize(text, Colors.BOLD, force_color=self.force_color)
    
    def format_italic(self, text):
        """Format italic text"""
        return colorize(text, Colors.ITALIC, force_color=self.force_color)
    
    def format_strikethrough(self, text):
        """Format strikethrough text"""
        return colorize(text, Colors.DIM, force_color=self.force_color)