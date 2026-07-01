"""
Output formatters for markdown elements
Handles rendering of headings, code, tables, lists, and more
"""

import re
from pygments import highlight
from pygments.lexers import get_lexer_by_name, TextLexer
from pygments.formatters import Terminal256Formatter
try:
    import emoji as emoji_lib
except ImportError:
    emoji_lib = None

from .colors import colorize, Colors, get_terminal_width


class MarkdownFormatter:
    """Formats markdown elements for terminal output"""
    
    def __init__(self, theme_config, inline_code_color=None, code_background=False, width=None, force_color=False, dim_mode=False):
        """
        Initialize formatter
        
        Args:
            theme_config: Theme configuration dict
            inline_code_color: Custom color for inline code (default from theme)
            code_background: Whether to show background in code blocks
            width: Terminal width (auto-detect if None)
            force_color: Whether to force color output
            dim_mode: Whether to use dim mode
        """
        self.theme = theme_config
        self.inline_code_color = inline_code_color or theme_config['inline_code']
        self.code_background = code_background
        self.width = width or get_terminal_width()
        self.force_color = force_color
        self.dim_mode = dim_mode

    def _colorize(self, text, color_code):
        """Wrap colorize with instance-level force_color and dim_mode settings"""
        return colorize(text, color_code, force_color=self.force_color, dim_mode=self.dim_mode)
    
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
            text = self._colorize(f'{marker}{text}', color + Colors.BOLD)
            return f'\n{text}\n'
        elif level == 2:
            marker = '## '
            text = self._colorize(f'{marker}{text}', color + Colors.BOLD)
            return f'\n{text}\n'
        else:
            marker = '#' * level + ' '
            text = self._colorize(f'{marker}{text}', color)
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
        try:
            if language:
                lexer = get_lexer_by_name(language, stripall=False)
            else:
                lexer = TextLexer()
        except Exception:
            lexer = TextLexer()
        
        # Format code with pygments
        try:
            formatter = Terminal256Formatter(style=self.theme.get('pygments_style', 'monokai'))
        except Exception:
            formatter = Terminal256Formatter(style='monokai')
        highlighted = highlight(code, lexer, formatter).rstrip()
        
        # Add line numbers if requested
        if line_numbers:
            lines = highlighted.split('\n')
            max_line_num = len(lines)
            num_width = len(str(max_line_num))
            
            formatted_lines = []
            for i, line in enumerate(lines, 1):
                line_num = self._colorize(f'{i:>{num_width}}', Colors.BRIGHT_BLACK)
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
        return self._colorize(f'`{text}`', self.inline_code_color)
    
    def format_table(self, rows):
        if not rows:
            return ''

        max_cols = max(len(row) for row in rows)

        normalized_rows = []
        for row in rows:
            normalized_row = list(row) + [''] * (max_cols - len(row))
            normalized_rows.append(normalized_row)

        col_widths = [0] * max_cols
        for row in normalized_rows:
            for i, cell in enumerate(row):
                clean_cell = re.sub(r'\033\[[0-9;]*m', '', str(cell))
                col_widths[i] = max(col_widths[i], len(clean_cell))

        total_border_chars = max_cols * 3 + 1
        total_table_width = sum(col_widths) + total_border_chars
        max_width = self.width - 2

        if total_table_width > max_width:
            available = max_width - total_border_chars
            widths_sum = sum(col_widths)
            if available < max_cols:
                col_widths = [max(1, available // max_cols)] * max_cols
            else:
                for i in range(max_cols):
                    col_widths[i] = max(1, col_widths[i] * available // widths_sum)

        border_color = self.theme['table_border']
        header_color = self.theme.get('table_header')
        formatted = []

        for row_idx, row in enumerate(normalized_rows):
            padded = []
            for i, cell in enumerate(row):
                clean_cell = re.sub(r'\033\[[0-9;]*m', '', str(cell))
                if len(clean_cell) > col_widths[i]:
                    cell_str = clean_cell[:col_widths[i] - 1] + '…'
                    if row_idx == 0 and header_color:
                        cell_str = self._colorize(cell_str, header_color + Colors.BOLD)
                else:
                    cell_str = str(cell)
                    padding = col_widths[i] - len(clean_cell)
                    if padding:
                        cell_str = cell_str + ' ' * padding
                    if row_idx == 0 and header_color:
                        cell_str = self._colorize(cell_str, header_color + Colors.BOLD)
                padded.append(cell_str)

            cells_formatted = [f' {cell} ' for cell in padded]
            row_str = self._colorize('│', border_color) + self._colorize('│', border_color).join(cells_formatted) + self._colorize('│', border_color)
            formatted.append(row_str)

            if row_idx == 0:
                sep_parts = []
                for w in col_widths:
                    sep_parts.append('─' * (w + 2))
                sep = self._colorize('├' + '┼'.join(sep_parts) + '┤', border_color)
                formatted.append(sep)

        top_parts = ['─' * (w + 2) for w in col_widths]
        top = self._colorize('┌' + '┬'.join(top_parts) + '┐', border_color)
        bottom = self._colorize('└' + '┴'.join(top_parts) + '┘', border_color)

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
            marker = self._colorize(f'{number}.', Colors.BRIGHT_BLUE)
        else:
            marker = self._colorize('•', Colors.BRIGHT_BLUE)
        
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
            box = self._colorize('☑', self.theme['checkbox_checked'])
        else:
            box = self._colorize('☐', self.theme['checkbox_unchecked'])
        
        return f'{box}  {text}'
    
    def format_blockquote(self, text):
        border = self._colorize('│', self.theme['blockquote_border'])
        lines = text.split('\n')
        formatted = [f'{border} {line}' for line in lines]
        return '\n' + '\n'.join(formatted) + '\n'

    def format_alert(self, alert_type, text):
        alert_colors = self.theme.get('alert_colors', {})
        color = alert_colors.get(alert_type, Colors.BRIGHT_BLACK)
        label = self._colorize(f' {alert_type} ', color + Colors.BOLD)
        if not text:
            return '\n' + label + '\n'
        border = self._colorize('│', color)
        lines = text.split('\n')
        formatted = [f'{border} {line}' for line in lines]
        return '\n' + label + '\n' + '\n'.join(formatted) + '\n'

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
        colored_text = self._colorize(text, link_color + Colors.UNDERLINE)
        return f'{colored_text} ({self._colorize(url, Colors.DIM)})'
    
    def format_hr(self):
        line = '─' * self.width
        return '\n' + self._colorize(line, self.theme['hr']) + '\n'
    
    def format_image(self, alt_text, url):
        """
        Format image as styled alt text with URL
        
        Args:
            alt_text: Image alt text
            url: Image URL
        
        Returns:
            Formatted image string
        """
        img_color = self.theme.get('link', Colors.BRIGHT_CYAN)
        colored_alt = self._colorize(f'[{alt_text}]', img_color + Colors.ITALIC)
        return f'{colored_alt}({self._colorize(url, Colors.DIM)})'

    def format_code_line(self, line, language):
        """Format a single code line for streaming with per-line syntax highlighting"""
        try:
            if language:
                lexer = get_lexer_by_name(language, stripall=False)
            else:
                lexer = TextLexer()
            try:
                formatter = Terminal256Formatter(style=self.theme.get('pygments_style', 'monokai'))
            except Exception:
                formatter = Terminal256Formatter(style='monokai')
            highlighted = highlight(line, lexer, formatter).rstrip('\n')
        except Exception:
            highlighted = line
        return highlighted

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
        return self._colorize(text, Colors.BOLD)
    
    def format_italic(self, text):
        """Format italic text"""
        return self._colorize(text, Colors.ITALIC)
    
    def format_strikethrough(self, text):
        """Format strikethrough text"""
        return self._colorize(text, Colors.DIM)
