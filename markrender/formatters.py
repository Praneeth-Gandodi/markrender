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

try:
    from rich.table import Table
    from rich.console import Console, Group
    from rich.text import Text
    from rich.ansi import AnsiDecoder
    from rich.tree import Tree
    rich_available = True
except ImportError:
    Table = None
    Console = None
    Group = None
    Text = None
    AnsiDecoder = None
    Tree = None
    rich_available = False

from .colors import Colors, get_terminal_width, get_rich_color_style, colorize, rgb, get_color_system


class MarkdownFormatter:
    """Formats markdown elements for terminal output"""
    def __init__(self, theme_config, inline_code_color=None, code_background=False, width=None, force_color=False, output=None, dim_mode=False):
            """
            Initialize formatter

            Args:
                theme_config: Theme configuration dict
                inline_code_color: Custom color for inline code (default from theme)
                code_background: Whether to show background in code blocks
                width: Terminal width (auto-detect if None)
                force_color: Force color output (bypasses terminal capability check)
                output: Output file object (to determine if we should force colors)
                dim_mode: Enable dim mode (dimmed text, reduced colors)
            """
            self.theme = theme_config
            self.inline_code_color = inline_code_color or theme_config['inline_code']
            self.code_background = code_background
            self.width = width or get_terminal_width()
            self.force_color = force_color
            self.dim_mode = dim_mode
            self._line_counter = 0
            
            # Determine if we should force terminal features based on output
            should_force_terminal = self.force_color
            if output and not hasattr(output, 'isatty'):
                # If output doesn't have isatty (like StringIO), force terminal features for colors
                should_force_terminal = True
            elif output and hasattr(output, 'isatty'):
                should_force_terminal = output.isatty() or self.force_color
            
            if rich_available:
                # Detect supported color system
                color_system = get_color_system()
                if self.force_color:
                    color_system = "truecolor"
                
                # Only use StringIO if an output file is provided, otherwise use default (stdout)
                console_kwargs = {
                    'width': self.width,
                    'force_terminal': should_force_terminal,
                    'color_system': color_system,
                    'soft_wrap': False,
                    'tab_size': 4
                }
                if output:
                    console_kwargs['file'] = output
                
                self.console = Console(**console_kwargs)
                self.ansi_decoder = AnsiDecoder()
            else:
                self.console = None
                self.ansi_decoder = None

    def _apply_dim(self, style):
        """Helper to apply dimming to a style if dim_mode is enabled"""
        if not self.dim_mode:
            return style
        if not style:
            return "dim"
        # If it's a hex or rgb color, we might want to just prefix it with dim
        return f"dim {style}"
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
        
        # Get lexer for single line highlighting, fallback to TextLexer
        try:
            if language:
                lexer = get_lexer_by_name(language, stripall=True)
            else:
                lexer = TextLexer()
        except ClassNotFound:
            lexer = TextLexer()
        
        if self.dim_mode:
             # Use 256 color formatter with a simpler style for dim mode
             formatter = Terminal256Formatter(style='default')
        else:
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
        if self.dim_mode:
            highlighted_rich_text.stylize("dim")
        
        # Combine leading whitespace with highlighted content
        full_line = Text(leading_whitespace) + highlighted_rich_text

        if line_numbers:
            line_num_style = self._apply_dim(get_rich_color_style(Colors.BRIGHT_BLACK))
            # Use a fixed width (minimum 3) for streaming to avoid layout shifts
            # It will automatically expand if the line count exceeds 3 digits
            num_width = max(3, len(str(self._line_counter)))
            line_num_text = Text(f'{self._line_counter:>{num_width}}', style=line_num_style)
            if self.code_background and not self.dim_mode:
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
        rich_style = self._apply_dim(get_rich_color_style(color_code))
        
        if isinstance(text, str):
            rich_text = Text(text)
        else:
            rich_text = text.copy()

        rich_text.stylize(rich_style)
        
        # Different symbols for different heading levels
        if level <= 2:
            rich_text.stylize(self._apply_dim(get_rich_color_style(Colors.BOLD)))
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
        if self.dim_mode:
            formatter = Terminal256Formatter(style='default')
        else:
            formatter = TerminalTrueColorFormatter(style=self.theme.get('pygments_style', 'monokai'))
            
        highlighted_ansi = highlight(code, lexer, formatter).rstrip()
        
        # Convert ANSI to rich.Text
        highlighted_rich_text = Text.from_ansi(highlighted_ansi)
        if self.dim_mode:
            highlighted_rich_text.stylize("dim")
        
        # Add line numbers if requested
        if line_numbers:
            lines = highlighted_rich_text.split('\n')
            max_line_num = len(lines)
            num_width = max(3, len(str(max_line_num)))
            
            formatted_rich_lines = Text()
            for i, rich_line in enumerate(lines, 1):
                line_num_style = self._apply_dim(get_rich_color_style(Colors.BRIGHT_BLACK))
                line_num_text = Text(f'{i:>{num_width}}', style=line_num_style)
                # Add background if requested
                if self.code_background and not self.dim_mode:
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
        style = self._apply_dim(get_rich_color_style(self.inline_code_color))
        return Text(text, style=style)

    def format_file_tree(self, tree_data: str) -> Group:
        """
        Format a file tree from string representation.
        
        Args:
            tree_data: String representation of a file tree
            
        Returns:
            Rich object representing the tree
        """
        if not rich_available or not Tree:
            return Text(tree_data)

        lines = tree_data.strip().split('\n')
        if not lines:
            return Text("")

        # Extract root
        root_name = lines[0].strip()
        tree = Tree(root_name, guide_style=self._apply_dim("bright_black"))

        # Map to keep track of nodes at different indentation levels
        # level -> node
        nodes = {0: tree}
        
        for line in lines[1:]:
            # Determine level based on characters like │, ├, └ or spaces
            # This is a heuristic for common tree outputs
            stripped = line.lstrip(' │├└─')
            indent = len(line) - len(stripped)
            level = indent // 4 + 1 # Assuming 4 spaces per level heuristic
            
            # More robust level detection for │   ├─ style
            level = 0
            for char in line:
                if char in '│├└ ':
                    level += 1
                else:
                    break
            level = (level // 4) + 1
            
            # Find parent node
            parent_level = level - 1
            while parent_level >= 0 and parent_level not in nodes:
                parent_level -= 1
            
            if parent_level >= 0:
                parent_node = nodes[parent_level]
                
                # Determine icon
                icon = "📄"
                style = "white"
                if "." not in stripped: # Likely a directory
                    icon = "📁"
                    style = "blue"
                
                style = self._apply_dim(style)
                label = Text.assemble((f"{icon} ", style), (stripped, style))
                new_node = parent_node.add(label)
                nodes[level] = new_node

        return Group(Text("\n"), tree, Text("\n"))
    

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
             table_border_style = self._apply_dim(rich_border_color if rich_border_color else "none")
        else:
             table_border_style = self._apply_dim("none")

        # table_header is now an ANSI color code, convert to rich style
        header_color_code = self.theme.get('table_header')
        if header_color_code:
            rich_header_color = get_rich_color_style(header_color_code)
            header_style = self._apply_dim(f"bold {rich_header_color}" if rich_header_color else "bold magenta")
        else:
            header_style = self._apply_dim("bold magenta")

        table = Table(show_header=True, header_style=header_style, border_style=table_border_style, padding=(0, 1))

        # Add columns
        for col_title in header:
            if self.dim_mode and isinstance(col_title, Text):
                 col_title.stylize("dim")
            table.add_column(col_title)

        # Add data rows with empty rows between for spacing
        for i, row_data in enumerate(data_rows):
            if self.dim_mode:
                for cell in row_data:
                    if isinstance(cell, Text):
                        cell.stylize("dim")
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
        marker_color = self.theme.get('list_marker', Colors.BRIGHT_BLUE)
        marker_style = self._apply_dim(get_rich_color_style(marker_color))
        
        if ordered:
            marker = Text(f'{number}.', style=marker_style)
        else:
            # Cycle through different bullet types for levels
            bullets = ['●', '○', '■', '▫']
            bullet = bullets[indent_level % len(bullets)]
            marker = Text(bullet, style=marker_style)
        
        if isinstance(text, str):
            text_obj = Text.from_markup(text)
        else:
            text_obj = text
            
        if self.dim_mode:
            text_obj.stylize("dim")
            
        return Text.assemble(indent, marker, " ", text_obj)
    
    def format_checkbox(self, checked, text: Text) -> Text:
        """
        Format checkbox (task list item)
        """
        if checked:
            box_style = self._apply_dim(get_rich_color_style(self.theme['checkbox_checked']))
            box = Text('✅', style=box_style)
        else:
            box_style = self._apply_dim(get_rich_color_style(self.theme['checkbox_unchecked']))
            box = Text('⬜', style=box_style)

        text_obj = Text.from_markup(text) if isinstance(text, str) else text
        if self.dim_mode:
            text_obj.stylize("dim")
            
        return Text.assemble(box, "  ", text_obj)

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
        if self.dim_mode:
            bar_color = "white"
            status_icon = '•'
        elif percentage >= 100:
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
        result.append(f'{status_icon} [', style=self._apply_dim(get_rich_color_style(Colors.BRIGHT_BLACK)))
        result.append(bar, style=self._apply_dim(get_rich_color_style(bar_color)))
        result.append(f'] {percentage_str}', style=self._apply_dim(get_rich_color_style(Colors.BRIGHT_BLACK)))
        result.append(' ')
        
        if isinstance(text, Text):
            text_obj = text
        else:
            text_obj = Text(str(text))
            
        if self.dim_mode:
            text_obj.stylize("dim")
            
        result.append(text_obj)
        
        return result
    
    def format_blockquote(self, lines_data: list[tuple[str, int]]) -> Text:
        """
        Format blockquote with border or callout box.
        """
        if not lines_data:
            return Text("")

        # Helper to get callout type from the first line
        first_line_content, base_nesting_level = lines_data[0]
        # Ensure it's string for regex
        stripped_first_line = str(first_line_content).strip()

        # Check for callout syntax: [!TYPE] Content or NOTE: content
        callout_match = re.match(r'^\[?(NOTE|TIP|IMPORTANT|WARNING|CAUTION|ATTENTION|INFO|SUCCESS|QUESTION|FAILURE|BUG|EXAMPLE|QUOTE)\]?\s*[:\-]?\s*(.*)', stripped_first_line, re.IGNORECASE)

        if callout_match:
            callout_type = callout_match.group(1).upper()
            message_first_line = callout_match.group(2).strip()

            # Callout colors - professional color scheme
            callout_colors = {
                "NOTE": rgb(59, 130, 246),       # Blue
                "TIP": rgb(34, 197, 94),         # Green
                "IMPORTANT": rgb(168, 85, 247),  # Purple
                "WARNING": rgb(251, 191, 36),    # Yellow
                "CAUTION": rgb(239, 68, 68),     # Red
                "ATTENTION": rgb(239, 68, 68),   # Red
                "INFO": rgb(59, 130, 246),       # Blue
                "SUCCESS": rgb(34, 197, 94),     # Green
                "QUESTION": rgb(59, 130, 246),   # Blue
                "FAILURE": rgb(239, 68, 68),     # Red
                "BUG": rgb(239, 68, 68),         # Red
                "EXAMPLE": rgb(107, 114, 128),   # Gray
                "QUOTE": rgb(107, 114, 128),     # Gray
            }
            
            if self.dim_mode:
                type_color = "white" # Simple color for dim mode
            else:
                type_color = callout_colors.get(callout_type, rgb(107, 114, 128))

            # Title case for display
            type_display = callout_type.capitalize()

            # Format the callout header with colored bar
            assembled_lines = []

            # Indentation for the block itself
            indent_str = '  ' * max(0, base_nesting_level - 1)

            # Styles
            border_style = self._apply_dim(get_rich_color_style(type_color))
            header_text_style = self._apply_dim(get_rich_color_style(type_color) + " bold")

            # Top border
            header_bar = Text.assemble(
                Text(indent_str),
                Text("┌", style=border_style),
                Text("─" * 6, style=border_style),
                Text(f" {type_display} ", style=header_text_style),
                Text("─" * 40, style=border_style),
                Text("┐", style=border_style),
            )
            assembled_lines.append(header_bar)

            # First line content
            if message_first_line:
                content_text = Text.from_markup(message_first_line) if isinstance(message_first_line, str) else Text(str(message_first_line))
                if self.dim_mode:
                    content_text.stylize("dim")
                    
                first_line_text = Text.assemble(
                    Text(indent_str + "│  ", style=border_style),
                    content_text
                )
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

                if self.dim_mode:
                    content_text.stylize("dim")
                    
                line_text = Text.assemble(
                    Text(current_indent),
                    Text("│  ", style=border_style),
                    content_text
                )
                assembled_lines.append(line_text)

            # Bottom border
            footer_bar = Text.assemble(
                Text(indent_str),
                Text("└", style=border_style),
                Text("─" * (56 + len(type_display)), style=border_style),
                Text("┘", style=border_style),
            )
            assembled_lines.append(footer_bar)

            return Text.assemble(*assembled_lines, "\n")

        # Standard Blockquote Rendering with Nesting Support
        assembled_text = Text()
        border_char = '│'
        border_style = self._apply_dim(get_rich_color_style(self.theme['blockquote_border']))

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

            if self.dim_mode:
                content.stylize("dim")
                
            assembled_text.append(Text.assemble(prefix, content))

            if i < len(lines_data) - 1:
                assembled_text.append("\n")

        return assembled_text
    
    def format_link(self, text: str, url: str) -> Text:
        """
        Format link with enhanced visual styling and OSC 8 support.
        
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
        link_color = self.theme.get('link', Colors.BLUE)
        link_style = get_rich_color_style(link_color)
        
        # If in dim mode, we use a much simpler style
        if self.dim_mode:
            result = Text()
            result.append(text, style="dim underline")
            # Apply OSC 8 link to the text if possible
            result.stylize(f"link {url}")
            result.append(f" ({url})", style="dim")
            return result
            
        result = Text()
        result.append(f"{icon} ", style=get_rich_color_style(Colors.BRIGHT_BLACK))
        
        # Create the clickable part
        link_text = Text(text, style=f"{link_style} underline")
        link_text.stylize(f"link {url}")
        result.append(link_text)
        
        # Add a nice tooltip-like URL if it's not too long
        if len(url) < 50:
             result.append(f" ({url})", style=get_rich_color_style(Colors.BRIGHT_BLACK))
        else:
             result.append(f" ({url[:47]}...)", style=get_rich_color_style(Colors.BRIGHT_BLACK))
        
        return result
    
    def format_hr(self) -> Text:
        """
        Format horizontal rule
        """
        width = min(self.width, 80)
        line = '─' * width
        style = self._apply_dim(get_rich_color_style(self.theme['hr']))
        return Text.assemble("\n", Text(line, style=style), "\n")
    
    def format_emoji(self, emoji_code: str) -> Text:
        """
        Convert emoji code to emoji character, with robust fallback.
        
        Args:
            emoji_code: Emoji code without colons (e.g., 'wave' for :wave:)
            
        Returns:
            Text object with emoji or fallback
        """
        if emoji_lib:
            try:
                # Try with alias first
                char = emoji_lib.emojize(f':{emoji_code}:', language='alias')
                # Check if it actually returned an emoji (not the original code)
                if char != f':{emoji_code}:':
                    return Text(char)
            except Exception:
                pass
            
            # Try with full emoji name
            try:
                char = emoji_lib.emojize(f':{emoji_code}:')
                if char != f':{emoji_code}:':
                    return Text(char)
            except Exception:
                pass
        
        # Fallback: return the code in a nice format
        return Text(f':{emoji_code}:', style=get_rich_color_style(Colors.YELLOW))

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

    def format_latex(self, latex: str, display: bool = False) -> str:
        """
        Format LaTeX math expression as Unicode/ASCII representation.
        
        Args:
            latex: LaTeX math expression
            display: Whether this is display math (centered, on its own line)
            
        Returns:
            Formatted math string
        """
        # Clean up the LaTeX
        latex = latex.strip()
        
        # Simple substitutions for common math symbols
        substitutions = {
            r'\\alpha': 'α', r'\\beta': 'β', r'\\gamma': 'γ', r'\\delta': 'δ',
            r'\\epsilon': 'ε', r'\\zeta': 'ζ', r'\\eta': 'η', r'\\theta': 'θ',
            r'\\iota': 'ι', r'\\kappa': 'κ', r'\\lambda': 'λ', r'\\mu': 'μ',
            r'\\nu': 'ν', r'\\xi': 'ξ', r'\\pi': 'π', r'\\rho': 'ρ',
            r'\\sigma': 'σ', r'\\tau': 'τ', r'\\upsilon': 'υ', r'\\phi': 'φ',
            r'\\chi': 'χ', r'\\psi': 'ψ', r'\\omega': 'ω',
            r'\\Alpha': 'Α', r'\\Beta': 'Β', r'\\Gamma': 'Γ', r'\\Delta': 'Δ',
            r'\\Epsilon': 'Ε', r'\\Zeta': 'Ζ', r'\\Eta': 'Η', r'\\Theta': 'Θ',
            r'\\Iota': 'Ι', r'\\Kappa': 'Κ', r'\\Lambda': 'Λ', r'\\Mu': 'Μ',
            r'\\Nu': 'Ν', r'\\Xi': 'Ξ', r'\\Pi': 'Π', r'\\Rho': 'Ρ',
            r'\\Sigma': 'Σ', r'\\Tau': 'Τ', r'\\Upsilon': 'Υ', r'\\Phi': 'Φ',
            r'\\Chi': 'Χ', r'\\Psi': 'Ψ', r'\\Omega': 'Ω',
            r'\\infty': '∞', r'\\partial': '∂', r'\\nabla': '∇', r'\\sqrt': '√',
            r'\\int': '∫', r'\\sum': '∑', r'\\prod': '∏', r'\\cdot': '·',
            r'\\times': '×', r'\\div': '÷', r'\\pm': '±', r'\\leq': '≤',
            r'\\geq': '≥', r'\\neq': '≠', r'\\approx': '≈', r'\\equiv': '≡',
            r'\\in': '∈', r'\\notin': '∉', r'\\subset': '⊂', r'\\supset': '⊃',
            r'\\cup': '∪', r'\\cap': '∩', r'\\emptyset': '∅', r'\\forall': '∀',
            r'\\exists': '∃', r'\\neg': '¬', r'\\wedge': '∧', r'\\vee': '∨',
            r'\\rightarrow': '→', r'\\leftarrow': '←', r'\\Rightarrow': '⇒',
            r'\\Leftarrow': '⇐', r'\\leftrightarrow': '↔', r'\\circ': '∘',
            r'\\degree': '°', r'\\^\\circ': '°',
            r'\\frac': '',  # Will handle fractions specially
            r'\\left': '', r'\\right': '',
            r'\\{': '{', r'\\}': '}', r'\\ ': ' ',
        }
        
        result = latex
        
        # Handle fractions: \frac{a}{b} → a/b
        import re
        frac_pattern = r'\\frac\{([^}]+)\}\{([^}]+)\}'
        def replace_frac(match):
            num = match.group(1)
            den = match.group(2)
            return f'({num})/({den})'
        result = re.sub(frac_pattern, replace_frac, result)
        
        # Handle superscripts: x^{2} → x²
        sup_pattern = r'\^\{([^}]+)\}'
        sup_replacements = {'2': '²', '3': '³', 'n': 'ⁿ', 'T': 'ᵀ'}
        def replace_sup(match):
            sup = match.group(1)
            return sup_replacements.get(sup, f'^{sup}')
        result = re.sub(sup_pattern, replace_sup, result)
        
        # Handle subscripts: x_{i} → xᵢ
        sub_pattern = r'_\{([^}]+)\}'
        sub_replacements = {'i': 'ᵢ', 'j': 'ⱼ', 'k': 'ₖ', 'n': 'ₙ', 'x': 'ₓ'}
        def replace_sub(match):
            sub = match.group(1)
            return sub_replacements.get(sub, f'_{sub}')
        result = re.sub(sub_pattern, replace_sub, result)
        
        # Apply other substitutions
        for latex_sym, unicode_char in substitutions.items():
            result = result.replace(latex_sym, unicode_char)
        
        # Remove remaining backslashes for unknown commands
        result = re.sub(r'\\[a-zA-Z]+', '', result)
        
        # Format for display or inline
        if display:
            return f'\n  {result}  \n'
        else:
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
        Format Mermaid diagram as ASCII/Unicode art with improved rendering.
        
        Args:
            code: Mermaid diagram code
            
        Returns:
            Formatted diagram Text object
        """
        result = Text()
        
        # Parse the mermaid code to extract nodes and edges
        try:
            nodes, edges, graph_type = self._parse_mermaid(code)
        except Exception:
            # Fallback for parsing errors
            nodes, edges, graph_type = {}, [], 'TD'
        
        if not nodes:
            # Better fallback for empty or unparseable diagrams
            title_style = self._apply_dim(get_rich_color_style(Colors.BOLD))
            border_style = self._apply_dim(get_rich_color_style(Colors.BRIGHT_BLACK))
            
            result.append("\n")
            result.append("┌" + "─" * 50 + "┐\n", style=border_style)
            result.append("│", style=border_style)
            result.append(" Mermaid Diagram ".center(50), style=title_style)
            result.append("│\n", style=border_style)
            result.append("├" + "─" * 50 + "┤\n", style=border_style)
            
            # Show original code as fallback if it's small enough
            code_lines = code.strip().split('\n')
            if len(code_lines) < 10:
                for line in code_lines:
                    result.append("│ ", style=border_style)
                    result.append(line.ljust(48), style=self._apply_dim("white"))
                    result.append(" │\n", style=border_style)
            else:
                result.append("│", style=border_style)
                result.append("  (Diagram too complex for terminal rendering)  ".center(50), style=self._apply_dim("white"))
                result.append("│\n", style=border_style)
                
            result.append("└" + "─" * 50 + "┘\n", style=border_style)
            return result
        
        # Calculate layout based on graph type
        if graph_type in ['LR', 'RL']:
            # Horizontal layout
            return self._render_horizontal_mermaid(nodes, edges, result)
        else:
            # Vertical layout (TD, TB, BT)
            return self._render_vertical_mermaid(nodes, edges, result)

    def _render_vertical_mermaid(self, nodes, edges, result: Text) -> Text:
        """Render mermaid diagram in vertical layout"""
        node_list = list(nodes.items())
        # Multi-edge support
        edge_map = {}
        for start, end in edges:
            if start not in edge_map:
                edge_map[start] = []
            edge_map[start].append(end)
        
        border_style = self._apply_dim(get_rich_color_style(Colors.BRIGHT_BLACK))
        text_style = self._apply_dim(get_rich_color_style(Colors.WHITE))
        
        for i, (node_id, label) in enumerate(node_list):
            # Node box
            box_width = max(len(label) + 4, 14)
            result.append("┌" + "─" * box_width + "┐\n", style=border_style)
            result.append("│ ", style=border_style)
            result.append(label.center(box_width - 2), style=text_style)
            result.append(" │\n", style=border_style)
            result.append("└" + "─" * box_width + "┘\n", style=border_style)
            
            # Edges from this node
            if node_id in edge_map:
                targets = edge_map[node_id]
                for j, target in enumerate(targets):
                    # Find target index to see if it's the next one
                    target_idx = -1
                    for idx, (nid, _) in enumerate(node_list):
                        if nid == target:
                            target_idx = idx
                            break
                    
                    if target_idx == i + 1:
                        # Direct connection to next
                        result.append("    │\n", style=border_style)
                        result.append("    ▼\n", style=border_style)
                    else:
                        # Jump connection
                        target_label = nodes.get(target, target)
                        result.append(f"    │ ➔ {target_label}\n", style=border_style)
            elif i < len(node_list) - 1:
                # Default flow if no edges defined but multiple nodes
                result.append("    │\n", style=border_style)
                result.append("    ▼\n", style=border_style)
        
        return result
    
    def _render_horizontal_mermaid(self, nodes, edges, result: Text) -> Text:
        """Render mermaid diagram in horizontal layout"""
        node_list = list(nodes.items())
        # Multi-edge support
        edge_map = {}
        for start, end in edges:
            if start not in edge_map:
                edge_map[start] = []
            edge_map[start].append(end)
        
        border_style = self._apply_dim(get_rich_color_style(Colors.BRIGHT_BLACK))
        text_style = self._apply_dim(get_rich_color_style(Colors.WHITE))
        
        # Build single line
        line = Text()
        for i, (node_id, label) in enumerate(node_list):
            # Node box
            box_width = max(len(label) + 4, 12)
            line.append("┌" + "─" * box_width + "┐", style=border_style)
            
            if i < len(node_list) - 1:
                line.append("─", style=border_style)
                line.append("▶", style=border_style)
                line.append("─", style=border_style)
        
        result.append("\n")
        result.append(line)
        result.append("\n")
        
        # Second line with labels
        label_line = Text()
        for node_id, label in node_list:
            box_width = max(len(label) + 4, 12)
            label_line.append("│ ", style=border_style)
            label_line.append(label.center(box_width - 2), style=text_style)
            label_line.append(" │", style=border_style)
            if node_id in edge_map:
                label_line.append("   ", style=border_style)
        
        result.append(label_line)
        result.append("\n")
        
        # Third line with bottom border
        border_line = Text()
        for i, (node_id, label) in enumerate(node_list):
            box_width = max(len(label) + 4, 12)
            border_line.append("└" + "─" * box_width + "┘", style=border_style)
            if i < len(node_list) - 1:
                border_line.append("   ", style=border_style)
        
        result.append(border_line)
        result.append("\n")
        
        return result
    
    def _parse_mermaid(self, code: str) -> tuple:
        """
        Parse Mermaid code and extract nodes, edges, and graph type.
        
        Args:
            code: Mermaid diagram code
            
        Returns:
            Tuple of (nodes dict, edges list, graph_type)
        """
        import re
        lines = code.strip().split('\n')
        
        # Determine graph type
        graph_type = 'TD'  # Default top-down
        for line in lines:
            line = line.strip()
            if line.startswith('graph ') or line.startswith('flowchart '):
                match = re.match(r'(?:graph|flowchart)\s*(TD|TB|BT|LR|RL)?', line, re.IGNORECASE)
                if match and match.group(1):
                    graph_type = match.group(1).upper()
                break
        
        # Parse nodes and edges
        nodes = {}
        edges = []
        
        content_lines = [l for l in lines if not l.strip().startswith('graph ') and not l.strip().startswith('flowchart ') and not l.strip().startswith('%%')]
        
        for line in content_lines:
            line = line.strip()
            if not line:
                continue
            
            # Find all nodes: A[Label], A(Label), A{Label}, A((Label))
            node_pattern = r'(\w+)(?:[\[\(\{]([^)\]\}]+)[\]\)\}]|\((\w+)\))'
            for match in re.finditer(node_pattern, line):
                node_id = match.group(1)
                node_label = match.group(2) if match.group(2) else (match.group(3) if match.group(3) else node_id)
                # Skip keywords
                if node_id.lower() not in ['to', 'and', 'or', 'if', 'then', 'else', 'subgraph', 'end']:
                    nodes[node_id] = node_label
            
            # Find edges: -->, -.->, ==>
            edge_pattern = r'(\w+)\s*(?:-+>|[.-]+>+|=+>)\s*(\w+)'
            for match in re.finditer(edge_pattern, line):
                edges.append((match.group(1), match.group(2)))
        
        return nodes, edges, graph_type
    
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