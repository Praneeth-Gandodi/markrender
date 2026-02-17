"""
Output formatters for markdown elements
Handles rendering of headings, code, tables, lists, and more
"""

import re
from pygments import highlight
from pygments.lexers import get_lexer_by_name, TextLexer
from pygments.formatters import Terminal256Formatter, TerminalTrueColorFormatter
from pygments.util import ClassNotFound
try:
    import emoji as emoji_lib
except ImportError:
    emoji_lib = None

# Imports for Rich library
from rich.table import Table
from rich.console import Console, Group
from rich.text import Text
from rich.ansi import AnsiDecoder
from io import StringIO
rich_available = True # Assuming rich is installed based on pyproject.toml

from .colors import Colors, get_terminal_width, get_rich_color_style, colorize, rgb


class MarkdownFormatter:
    """Formats markdown elements for terminal output"""
    def __init__(self, theme_config, inline_code_color=None, code_background=False, width=None, force_color=False, output=None):
            """
            Initialize formatter

            Args:
                theme_config: Theme configuration dict
                inline_code_color: Custom color for inline code (default from theme)
                code_background: Whether to show background in code blocks
                width: Terminal width (auto-detect if None)
                force_color: Force color output (bypasses terminal capability check)
                output: Output file object (to determine if we should force colors)
            """
            self.theme = theme_config
            self.inline_code_color = inline_code_color or theme_config['inline_code']
            self.code_background = code_background
            self.width = width or get_terminal_width()
            self.force_color = force_color
            self._line_counter = 0
            
            # Determine if we should force terminal features based on output
            should_force_terminal = self.force_color
            if output and not hasattr(output, 'isatty'):
                # If output doesn't have isatty (like StringIO), force terminal features for colors
                should_force_terminal = True
            elif output and hasattr(output, 'isatty'):
                should_force_terminal = output.isatty() or self.force_color
            
            if rich_available:
                # Force color system to truecolor to ensure RGB colors are used
                # Only use StringIO if an output file is provided, otherwise use default (stdout)
                console_kwargs = {
                    'width': self.width,
                    'force_terminal': should_force_terminal,
                    'color_system': "truecolor"  # Force truecolor support to ensure RGB codes
                }
                if output:
                    console_kwargs['file'] = output
                
                self.console = Console(**console_kwargs) # Keep force_terminal as it's a useful override
                self.ansi_decoder = AnsiDecoder()
            else:
                self.console = None
                self.ansi_decoder = None
    def start_code_block(self, language='', line_numbers=True):
        self._line_counter = 0
        from rich.text import Text
        if language:
            # Use Rich Text for consistent formatting
            rich_style = get_rich_color_style(Colors.BRIGHT_MAGENTA)
            return Text(f'\n{language}\n', style=rich_style)
        return Text('\n')

    def stream_code_line(self, line, language='', line_numbers=True):
        self._line_counter += 1
        num_width = len(str(self._line_counter))
        
        # Get lexer for single line highlighting, fallback to TextLexer
        try:
            if language:
                lexer = get_lexer_by_name(language, stripall=True)
            else:
                lexer = TextLexer()
        except ClassNotFound:
            lexer = TextLexer()
        
        formatter = TerminalTrueColorFormatter(style=self.theme.get('pygments_style', 'monokai'))
        
        # Preserve leading whitespace for indentation
        leading_whitespace = ''
        if line:
            match = re.match(r'^\s*', line)
            if match:
                leading_whitespace = match.group(0)

        highlighted_ansi = highlight(line.strip(), lexer, formatter).rstrip()
        
        # Convert Pygments ANSI output to rich.Text
        highlighted_rich_text = Text.from_ansi(highlighted_ansi)
        
        # Combine leading whitespace with highlighted content
        full_line = Text(leading_whitespace) + Text.from_ansi(highlighted_ansi)

        if line_numbers:
            line_num_text = Text(f'{self._line_counter:>{num_width}}', style=get_rich_color_style(Colors.BRIGHT_BLACK))
            if self.code_background:
                # Need to apply background to the line number Text object
                line_num_text.stylize(get_rich_color_style(Colors.BG_BRIGHT_BLACK))
                return Text.assemble(line_num_text, " ", full_line, "\n")
            else:
                return Text.assemble(" ", line_num_text, "  ", full_line, "\n")
        else:
            return Text.assemble(full_line, "\n")
    
    def end_code_block(self, language=''):
        self._line_counter = 0
        return '\n'
    
    def format_heading(self, level, text):
        """
        Format heading (H1-H6) with left justification and color
        
        Args:
            level: Heading level (1-6)
            text: Heading text (str or Text)
        
        Returns:
            Formatted heading rich.Text object
        """
        level = max(1, min(6, level))  # Clamp to 1-6
        color_code = self.theme['heading_colors'].get(level, Colors.WHITE)
        rich_style = get_rich_color_style(color_code)
        
        if isinstance(text, str):
            rich_text = Text(text)
        else:
            rich_text = text.copy()

        rich_text.stylize(rich_style)
        
        # Different symbols for different heading levels
        if level <= 2:
            rich_text.stylize(get_rich_color_style(Colors.BOLD))
            return Text.assemble("\n", rich_text, "\n")
        else:
            return Text.assemble("\n", rich_text, "\n")
    
    def format_code_block(self, code, language='', line_numbers=True):
        """
        Format code block with syntax highlighting
        
        Args:
            code: Code content
            language: Programming language for syntax highlighting
            line_numbers: Whether to show line numbers
        
        Returns:
            Formatted code block rich.Text object or string
        """
        # Get lexer
        try:
            if language:
                lexer = get_lexer_by_name(language, stripall=True)
            else:
                lexer = TextLexer()
        except ClassNotFound:
            lexer = TextLexer()
        
        # Format code with pygments to ANSI
        formatter = TerminalTrueColorFormatter(style=self.theme.get('pygments_style', 'monokai'))
        highlighted_ansi = highlight(code, lexer, formatter).rstrip()
        
        # Convert ANSI to rich.Text
        highlighted_rich_text = Text.from_ansi(highlighted_ansi)
        
        # Add line numbers if requested
        if line_numbers:
            lines = highlighted_rich_text.split('\n')
            max_line_num = len(lines)
            num_width = len(str(max_line_num))
            
            formatted_rich_lines = Text()
            for i, rich_line in enumerate(lines, 1):
                line_num_text = Text(f'{i:>{num_width}}', style=get_rich_color_style(Colors.BRIGHT_BLACK))
                # Add background if requested
                if self.code_background:
                    line_num_text.stylize(get_rich_color_style(Colors.BG_BRIGHT_BLACK))
                    formatted_rich_lines.append(Text.assemble(line_num_text, " ", rich_line, "\n"))
                else:
                    formatted_rich_lines.append(Text.assemble(" ", line_num_text, "  ", rich_line, "\n"))
            
            result = formatted_rich_lines
        else:
            result = highlighted_rich_text
        
        # Add spacing
        return Text.assemble("\n", result, "\n")
    
    def format_inline_code(self, text: str) -> Text:
        """
        Format inline code by returning a rich Text object.
        """
        style = get_rich_color_style(self.inline_code_color)
        return Text(text, style=style)
    

    def format_table(self, header, data_rows):
        """
        Format markdown table with borders using rich.

        Args:
            header: List of rich.Text or str for table header
            data_rows: List of lists of rich.Text or str representing table data rows

        Returns:
            Formatted table string or rich object
        """
        if not rich_available or not header:
            # Fallback to a simpler table format if rich is not available
            if not header:
                return ""
            header_line = " | ".join(str(h) for h in header)
            separator = "-" * len(header_line)
            data_lines = [" | ".join(str(c) for c in row) for row in data_rows]
            return '\n' + '\n'.join([header_line, separator] + data_lines) + '\n'

        # Initialize rich Table
        border_color_code = self.theme.get('table_border')
        if border_color_code and isinstance(border_color_code, str):
             # Try to convert if it's ANSI
             rich_border_color = get_rich_color_style(border_color_code)
             table_border_style = rich_border_color if rich_border_color else "none"
        else:
             table_border_style = "none"

        # table_header is now an ANSI color code, convert to rich style
        header_color_code = self.theme.get('table_header')
        if header_color_code:
            rich_header_color = get_rich_color_style(header_color_code)
            header_style = f"bold {rich_header_color}" if rich_header_color else "bold magenta"
        else:
            header_style = "bold magenta"

        table = Table(show_header=True, header_style=header_style, border_style=table_border_style, padding=(0, 1))

        # Add columns
        for col_title in header:
            table.add_column(col_title)

        # Add data rows with empty rows between for spacing
        for i, row_data in enumerate(data_rows):
            table.add_row(*row_data)
            # Add an empty row after each data row except the last one to create spacing
            if i < len(data_rows) - 1:
                # Create an empty row with empty cells to add visual spacing
                empty_row = ["" for _ in range(len(header))]
                table.add_row(*empty_row)

        # Return Group with spacing
        return Group(Text("\n"), table, Text("\n"))

    
    def format_list_item(self, text: Text, ordered=False, number=1, indent_level=0) -> Text:
        """
        Format list item (bullet or numbered)
        """
        indent = Text('  ' * indent_level)
        marker_style = get_rich_color_style(self.theme.get('list_marker', Colors.BRIGHT_BLUE))
        if ordered:
            marker = Text(f'{number}.', style=marker_style)
        else:
            marker = Text('•', style=marker_style)
        
        if isinstance(text, str):
            text_obj = Text.from_markup(text)
        else:
            text_obj = text
            
        return Text.assemble(indent, marker, " ", text_obj)
    
    def format_checkbox(self, checked, text: Text) -> Text:
        """
        Format checkbox (task list item)
        """
        if checked:
            box = Text('✅', style=get_rich_color_style(self.theme['checkbox_checked']))
        else:
            box = Text('⬜', style=get_rich_color_style(self.theme['checkbox_unchecked']))

        return Text.assemble(box, "  ", Text.from_markup(text) if isinstance(text, str) else text)

    def format_progress_bar(self, percentage: int, text: Text, indent_level: int = 0) -> Text:
        """
        Format progress bar task item (e.g., - [50%] Task name)
        
        Args:
            percentage: Progress percentage (0-100)
            text: Task description
            indent_level: Nesting level for indentation
            
        Returns:
            Formatted progress bar rich.Text object
        """
        indent = '  ' * indent_level
        
        # Create progress bar
        bar_width = 30
        filled = int(bar_width * percentage / 100)
        empty = bar_width - filled
        
        # Color based on progress
        if percentage >= 100:
            bar_color = self.theme.get('checkbox_checked', Colors.GREEN)
            status_icon = '✅'
        elif percentage >= 75:
            bar_color = rgb(100, 200, 100)  # Light green
            status_icon = '🟢'
        elif percentage >= 50:
            bar_color = rgb(255, 200, 0)  # Yellow
            status_icon = '🟡'
        elif percentage >= 25:
            bar_color = rgb(255, 150, 0)  # Orange
            status_icon = '🟠'
        else:
            bar_color = rgb(200, 100, 100)  # Red
            status_icon = '🔴'
        
        # Build progress bar string
        bar = '█' * filled + '░' * empty
        percentage_str = f'{percentage:3d}%'
        
        # Assemble the final text
        result = Text(indent)
        result.append(f'{status_icon} [', style=get_rich_color_style(Colors.BRIGHT_BLACK))
        result.append(bar, style=get_rich_color_style(bar_color))
        result.append(f'] {percentage_str}', style=get_rich_color_style(Colors.BRIGHT_BLACK))
        result.append(' ')
        
        if isinstance(text, Text):
            result.append(text)
        else:
            result.append(Text(str(text)))
        
        return result
    
    def format_blockquote(self, lines_data: list[tuple[str, int]]) -> Text:
        """
        Format blockquote with border
        """
        if not lines_data:
            return Text("")

        # Helper to get callout type from the first line
        first_line_content, base_nesting_level = lines_data[0]
        # Ensure it's string for regex
        stripped_first_line = str(first_line_content).strip()
        
        # Check for callout syntax: [!TYPE] Content
        callout_match = re.match(r'^\[!(NOTE|TIP|IMPORTANT|WARNING|CAUTION|ATTENTION|INFO|SUCCESS|QUESTION|FAILURE|BUG|EXAMPLE|QUOTE)\]\s*(.*)', stripped_first_line, re.IGNORECASE)

        if callout_match:
            callout_type = callout_match.group(1).upper()
            message_first_line = callout_match.group(2).strip()

            callout_colors = {
                "NOTE": self.theme.get('note_color', Colors.CYAN),
                "TIP": self.theme.get('tip_color', Colors.GREEN),
                "IMPORTANT": self.theme.get('important_color', Colors.MAGENTA),
                "WARNING": self.theme.get('warning_color', Colors.YELLOW),
                "CAUTION": self.theme.get('caution_color', Colors.RED),
                "ATTENTION": self.theme.get('attention_color', Colors.RED),
                "INFO": self.theme.get('info_color', Colors.BLUE),
                "SUCCESS": self.theme.get('success_color', Colors.GREEN),
                "QUESTION": self.theme.get('question_color', Colors.CYAN),
                "FAILURE": self.theme.get('failure_color', Colors.RED),
                "BUG": self.theme.get('bug_color', Colors.RED),
                "EXAMPLE": self.theme.get('example_color', Colors.WHITE),
                "QUOTE": self.theme.get('quote_color', Colors.WHITE),
            }
            type_color = callout_colors.get(callout_type, Colors.WHITE)

            # Icon mapping
            callout_icons = {
                "NOTE": "ℹ️",
                "TIP": "💡",
                "IMPORTANT": "‼",
                "WARNING": "⚠️",
                "CAUTION": "🛑",
                "ATTENTION": "🚨",
                "INFO": "📘",
                "SUCCESS": "✅",
                "QUESTION": "❓",
                "FAILURE": "❌",
                "BUG": "🐛",
                "EXAMPLE": "📝",
                "QUOTE": "💬",
            }
            icon = callout_icons.get(callout_type, "")

            # Format the callout header
            header_text = Text.assemble(
                Text(f"{icon} {callout_type}", style=get_rich_color_style(Colors.BOLD + type_color)),
                ": " if message_first_line else ""
            )
            
            assembled_lines = []
            
            # Indentation for the block itself
            indent_str = '  ' * max(0, base_nesting_level - 1)
            
            # First line
            first_line_text = Text.assemble(
                Text(indent_str), 
                header_text, 
                Text.from_markup(message_first_line) if isinstance(message_first_line, str) else message_first_line
            )
            # Apply color to the user's text as well (?) or just the bar?
            # Let's style the whole line
            # first_line_text.stylize(get_rich_color_style(type_color))
            # But header already has style.
            # Rich styling merges.
            assembled_lines.append(first_line_text)

            # Subsequent lines
            for i in range(1, len(lines_data)):
                line_content, line_level = lines_data[i]
                current_indent = '  ' * max(0, line_level - 1)

                # line_content may already be a Rich Text object with inline formatting applied
                if isinstance(line_content, Text):
                    content_text = line_content
                else:
                    content_text = Text.from_markup(line_content.strip()) if isinstance(line_content, str) else Text(str(line_content))
                
                line_text = Text.assemble(
                     Text(current_indent),
                     Text("  "),
                     content_text
                )
                # Don't override existing styling - just add color to unstyled portions
                line_text.stylize(get_rich_color_style(type_color), 0, len(current_indent) + 2)
                assembled_lines.append(line_text)

            return Text.assemble(*assembled_lines, "\n")

        # Standard Blockquote Rendering with Nesting Support
        assembled_text = Text()
        border_char = '│'
        border_style = get_rich_color_style(self.theme['blockquote_border'])

        for i, (line_str, line_level) in enumerate(lines_data):
            # For each nesting level, add a border char and space
            prefix = Text()
            for _ in range(max(1, line_level)):
                prefix.append(border_char, style=border_style)
                prefix.append(" ")

            # line_str may already be a Rich Text object with inline formatting applied
            if isinstance(line_str, Text):
                content = line_str
            else:
                content = Text.from_markup(line_str) if isinstance(line_str, str) else Text(str(line_str))
            
            assembled_text.append(Text.assemble(prefix, content))

            if i < len(lines_data) - 1:
                assembled_text.append("\n")
                
        return assembled_text
    
    def format_link(self, text: str, url: str) -> Text:
        """
        Format link with enhanced visual styling.
        
        Args:
            text: Link text
            url: Link URL
            
        Returns:
            Formatted link Text object with icon and styling
        """
        from rich.text import Text
        
        # Determine link icon based on URL type
        icon = "🔗"  # Default link icon
        if url.startswith('mailto:'):
            icon = "📧"
        elif url.startswith('tel:'):
            icon = "📞"
        elif 'github' in url.lower():
            icon = "🐙"
        elif url.startswith('https://'):
            icon = "🔒"  # Secure link
        elif url.startswith('http://'):
            icon = "🔓"  # Non-secure link
        
        # Create styled link text
        link_style = get_rich_color_style(self.theme.get('link', Colors.BLUE)) + " underline"
        
        result = Text()
        result.append(f"{icon} ", style=get_rich_color_style(Colors.BRIGHT_BLACK))
        result.append(text, style=link_style)
        result.append(f" ({url})", style=get_rich_color_style(Colors.BRIGHT_BLACK))
        
        return result
    
    def format_hr(self) -> Text:
        """
        Format horizontal rule
        """
        width = min(self.width, 80)
        line = '─' * width
        return Text.assemble("\n", Text(line, style=get_rich_color_style(self.theme['hr'])), "\n")
    
    def format_emoji(self, emoji_code: str) -> Text:
        """
        Convert emoji code to emoji character, with fallback.
        """
        if emoji_lib:
            try:
                char = emoji_lib.emojize(f':{emoji_code}:', language='alias')
                return Text(char)
            except Exception:
                pass
        return Text(f":{emoji_code}:", style=get_rich_color_style(Colors.YELLOW))

    def format_image(self, alt_text: str, url: str) -> str:
        """
        Format image as a placeholder with alt text and URL.
        
        Args:
            alt_text: Image alt text
            url: Image URL
            
        Returns:
            Formatted image placeholder string
        """
        # Create a visual image placeholder
        width = min(self.width - 4, 60)
        
        # Build the placeholder
        top_border = '╔' + '═' * width + '╗'
        
        # Icon and alt text
        icon = "🖼️"
        alt_display = alt_text if alt_text else "Image"
        if len(alt_display) > width - 6:
            alt_display = alt_display[:width - 9] + "..."
        
        middle_line = f'║ {icon}  {alt_display.center(width - 8)} ║'
        
        # URL (truncated if too long)
        url_display = url if len(url) <= width - 6 else url[:width - 9] + "..."
        url_line = f'║    {url_display.center(width - 8)} ║'
        
        bottom_border = '╚' + '═' * width + '╝'
        
        return f'\n{top_border}\n{middle_line}\n{url_line}\n{bottom_border}\n'

    def format_footnote_ref(self, footnote_id: str, footnote_num: int) -> Text:
        """
        Format footnote reference (superscript number).
        
        Args:
            footnote_id: Footnote identifier
            footnote_num: Footnote number in sequence
            
        Returns:
            Formatted footnote reference Text object
        """
        return Text(f'[{footnote_num}]', style=get_rich_color_style(self.theme.get('link', Colors.BLUE)) + " superscript")

    def format_footnotes_section(self, footnotes: list) -> Text:
        """
        Format the footnotes section at the end of the document.
        
        Args:
            footnotes: List of tuples (footnote_id, content, number)
            
        Returns:
            Formatted footnotes section Text object
        """
        if not footnotes:
            return Text("")
        
        result = Text("\n")
        result.append("─" * 40 + "\n", style=get_rich_color_style(Colors.BRIGHT_BLACK))
        result.append("Footnotes:\n", style=get_rich_color_style(Colors.BOLD))
        result.append("─" * 40 + "\n\n", style=get_rich_color_style(Colors.BRIGHT_BLACK))
        
        for footnote_id, content, num in footnotes:
            # Footnote marker
            result.append(f'[{num}] ', style=get_rich_color_style(self.theme.get('link', Colors.BLUE)) + " bold")
            
            # Footnote content
            if isinstance(content, Text):
                result.append(content)
            else:
                result.append(Text(str(content)))
            
            result.append("\n")
        
        return result

    def format_definition_item(self, term: Text, definition: Text) -> Text:
        """
        Format definition list item (Term : Definition).
        
        Args:
            term: Term text (formatted)
            definition: Definition text (formatted)
            
        Returns:
            Formatted definition item Text object
        """
        result = Text()
        
        # Term in bold
        if isinstance(term, Text):
            term_copy = term.copy()
            term_copy.stylize(get_rich_color_style(Colors.BOLD))
            result.append(term_copy)
        else:
            result.append(Text(str(term), style=get_rich_color_style(Colors.BOLD)))
        
        # Separator
        result.append(Text(" : ", style=get_rich_color_style(Colors.BRIGHT_BLACK)))
        
        # Definition
        if isinstance(definition, Text):
            result.append(definition)
        else:
            result.append(Text(str(definition)))
        
        return result

    def format_mermaid_diagram(self, code: str) -> Text:
        """
        Format Mermaid diagram as ASCII/Unicode art.
        
        Args:
            code: Mermaid diagram code
            
        Returns:
            Formatted diagram Text object
        """
        result = Text()
        
        # Add header
        result.append("\n", style=get_rich_color_style(Colors.BRIGHT_BLACK))
        result.append("┌", style=get_rich_color_style(Colors.BRIGHT_BLACK))
        result.append("─" * 50, style=get_rich_color_style(Colors.BRIGHT_BLACK))
        result.append("┐\n", style=get_rich_color_style(Colors.BRIGHT_BLACK))
        
        result.append("│", style=get_rich_color_style(Colors.BRIGHT_BLACK))
        result.append(" Mermaid Diagram ".center(50), style=get_rich_color_style(Colors.BOLD))
        result.append("│\n", style=get_rich_color_style(Colors.BRIGHT_BLACK))
        
        result.append("├", style=get_rich_color_style(Colors.BRIGHT_BLACK))
        result.append("─" * 50, style=get_rich_color_style(Colors.BRIGHT_BLACK))
        result.append("┤\n", style=get_rich_color_style(Colors.BRIGHT_BLACK))
        
        # Parse and render simple mermaid diagrams
        lines = self._parse_mermaid(code)
        for line in lines:
            result.append("│", style=get_rich_color_style(Colors.BRIGHT_BLACK))
            result.append(" " + line.ljust(50), style=get_rich_color_style(Colors.WHITE))
            result.append("│\n", style=get_rich_color_style(Colors.BRIGHT_BLACK))
        
        # Add footer
        result.append("└", style=get_rich_color_style(Colors.BRIGHT_BLACK))
        result.append("─" * 50, style=get_rich_color_style(Colors.BRIGHT_BLACK))
        result.append("┘\n", style=get_rich_color_style(Colors.BRIGHT_BLACK))
        
        return result
    
    def _parse_mermaid(self, code: str) -> list:
        """
        Parse Mermaid code and convert to ASCII representation.
        
        Args:
            code: Mermaid diagram code
            
        Returns:
            List of ASCII lines representing the diagram
        """
        lines = []
        code_lines = code.strip().split('\n')
        
        # Skip direction declaration
        content_lines = [l for l in code_lines if not l.strip().startswith('graph ') and not l.strip().startswith('flowchart ')]
        
        # Parse nodes and edges
        nodes = {}
        edges = []
        
        for line in content_lines:
            line = line.strip()
            if not line or line.startswith('%%'):
                continue
            
            # Parse node definitions like A[Label] or A(Label)
            import re
            # Find all nodes in the line (both sides of edges)
            node_matches = re.findall(r'(\w+)([\[\(]([^)\]]+)[\]\)])?', line)
            for match in node_matches:
                node_id = match[0]
                node_label = match[2] if match[2] else node_id
                if node_id and node_id not in ['to', 'and', 'or', 'if', 'then', 'else']:
                    nodes[node_id] = node_label
            
            # Parse edges like A --> B or A -.-> B
            edge_match = re.search(r'(\w+)\s*[-.]+[>]*\s*(\w+)', line)
            if edge_match:
                edges.append((edge_match.group(1), edge_match.group(2)))
        
        # Generate ASCII representation
        if not nodes:
            lines.append("  (No diagram content)")
            return lines
        
        # Simple vertical layout showing all nodes
        node_list = list(nodes.items())
        for i, (node_id, label) in enumerate(node_list):
            # Node box
            box_width = max(len(label) + 4, 12)
            lines.append("┌" + "─" * box_width + "┐")
            lines.append("│ " + label.center(box_width - 2) + " │")
            lines.append("└" + "─" * box_width + "┘")
            
            # Edge to next node
            if i < len(node_list) - 1:
                lines.append("    │")
                lines.append("    ▼")
        
        return lines
    
    def format_bold(self, text: str) -> Text:
        """Format bold text."""
        return Text(text, style=get_rich_color_style(Colors.BOLD))
    
    def format_italic(self, text: str) -> Text:
        """Format italic text."""
        return Text(text, style=get_rich_color_style(Colors.ITALIC))
    
    def format_strikethrough(self, text: str) -> Text:
        """Format strikethrough text."""
        return Text(text, style=get_rich_color_style(Colors.DIM) + " strike")

    def format_highlight(self, text: str) -> Text:
        """Format highlighted text."""
        return Text(text, style=get_rich_color_style(self.theme.get('highlight', Colors.YELLOW_BG)))