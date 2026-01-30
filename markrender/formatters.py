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
            marker = '# '
            text = colorize(f'{marker}{text}', color + Colors.BOLD)
            return f'\n{text}\n'
        elif level == 2:
            marker = '## '
            text = colorize(f'{marker}{text}', color + Colors.BOLD)
            return f'\n{text}\n'
        else:
            marker = '#' * level + ' '
            text = colorize(f'{marker}{text}', color)
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
        return colorize(f'`{text}`', self.inline_code_color)
    
    def format_table(self, rows):
        """
        Format markdown table with borders
        
        Args:
            rows: List of lists representing table rows
        
        Returns:
            Formatted table string
        """
        if not rows:
            return ''
        
        # Determine the maximum number of columns across all rows
        max_cols = max(len(row) for row in rows)
        
        # Normalize all rows to have the same number of columns
        normalized_rows = []
        for row in rows:
            # Pad row with empty strings if it has fewer columns
            normalized_row = list(row) + [''] * (max_cols - len(row))
            normalized_rows.append(normalized_row)
        
        # Calculate column widths
        col_widths = [0] * max_cols
        for row in normalized_rows:
            for i, cell in enumerate(row):
                # Strip ANSI codes for width calculation
                clean_cell = re.sub(r'\033\[[0-9;]*m', '', str(cell))
                col_widths[i] = max(col_widths[i], len(clean_cell))
        
        # Format rows
        border_color = self.theme['table_border']
        formatted = []
        
        for row_idx, row in enumerate(normalized_rows):
            # Pad cells
            padded = []
            for i, cell in enumerate(row):
                clean_cell = re.sub(r'\033\[[0-9;]*m', '', str(cell))
                padding = col_widths[i] - len(clean_cell)
                padded.append(str(cell) + ' ' * padding)
            
            # Create row
            row_str = colorize('│', border_color) + colorize(' ', border_color).join(
                f' {cell} ' for cell in padded
            ) + colorize('│', border_color)
            formatted.append(row_str)
            
            # Add separator after header (first row)
            if row_idx == 0:
                sep_parts = []
                for width in col_widths:
                    sep_parts.append('─' * (width + 2))
                sep = colorize('├' + '┼'.join(sep_parts) + '┤', border_color)
                formatted.append(sep)
        
        # Add top and bottom borders
        top_parts = ['─' * (w + 2) for w in col_widths]
        top = colorize('┌' + '┬'.join(top_parts) + '┐', border_color)
        bottom = colorize('└' + '┴'.join(top_parts) + '┘', border_color)
        
        return '\n' + top + '\n' + '\n'.join(formatted) + '\n' + bottom + '\n'
    
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
            box = colorize('☑', self.theme['checkbox_checked'])
        else:
            box = colorize('☐', self.theme['checkbox_unchecked'])
        
        return f'{box} {text}'
    
    def format_blockquote(self, text):
        """
        Format blockquote with border
        
        Args:
            text: Blockquote text
        
        Returns:
            Formatted blockquote string
        """
        border = colorize('│', self.theme['blockquote_border'])
        lines = text.split('\n')
        formatted = [f'{border} {line}' for line in lines]
        return '\n' + '\n'.join(formatted) + '\n'
    
    def format_link(self, text, url):
        """
        Format link with colored text and URL
        
        Args:
            text: Link text
            url: Link URL
        
        Returns:
            Formatted link string
        """
        link_color = self.theme['link']
        colored_text = colorize(text, link_color + Colors.UNDERLINE)
        return f'{colored_text} ({colorize(url, Colors.DIM)})'
    
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
