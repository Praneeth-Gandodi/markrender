"""
Main markdown renderer for streaming LLM responses
"""

import sys
from .parser import MarkdownParser
from .formatters import MarkdownFormatter
from .themes import get_theme
from .colors import get_terminal_width


class MarkdownRenderer:
    """
    Professional terminal markdown renderer for streaming LLM responses
    
    Example usage:
        renderer = MarkdownRenderer(theme='github-dark')
        
        for chunk in stream:
            content = chunk.choices[0].delta.content
            if content:
                renderer.render(content)
        
        renderer.finalize()
    """
    
    def __init__(
        self,
        theme='github-dark',
        code_background=False,
        inline_code_color=None,
        line_numbers=True,
        width=None,
        output=None
    ):
        """
        Initialize markdown renderer
        
        Args:
            theme: Syntax highlighting theme name (default: 'github-dark')
                   Available: github-dark, monokai, dracula, nord, one-dark,
                              solarized-dark, solarized-light
            code_background: Show background in code blocks (default: False)
            inline_code_color: Custom ANSI color for inline code (default: theme default)
            line_numbers: Show line numbers in code blocks (default: True)
            width: Terminal width (default: auto-detect)
            output: Output file object (default: sys.stdout)
        """
        self.theme_config = get_theme(theme)
        self.code_background = code_background
        self.line_numbers = line_numbers
        self.width = width or get_terminal_width()
        self.output = output or sys.stdout
        
        # Initialize parser and formatter
        self.parser = MarkdownParser()
        self.formatter = MarkdownFormatter(
            self.theme_config,
            inline_code_color=inline_code_color,
            code_background=code_background,
            width=self.width
        )
        
        # Buffer for incomplete content
        self.buffer = ''
        
        # State tracking
        self.in_code_block = False
        self.code_language = ''
        self.code_lines = []
        self.in_table = False
        self.table_rows = []
        self.in_blockquote = False
        self.blockquote_lines = []
    
    def render(self, chunk):
        """
        Render a chunk of markdown content
        
        Args:
            chunk: Markdown text chunk from streaming response
        """
        if not chunk:
            return
        
        # Add to buffer
        self.buffer += chunk
        
        # If we're in a code block, don't process line-by-line
        # Wait for the closing delimiter
        if self.in_code_block:
            # Check if we have the closing delimiter
            if '\n```' in self.buffer or self.buffer.endswith('```'):
                # Process everything up to and including the closing delimiter
                lines = self.buffer.split('\n')
                for line in lines:
                    if line.strip().startswith('```') and len(self.code_lines) > 0:
                        # Closing delimiter found
                        code = '\n'.join(self.code_lines)
                        formatted = self.formatter.format_code_block(
                            code,
                            self.code_language,
                            self.line_numbers
                        )
                        self._write(formatted)
                        self.in_code_block = False
                        self.code_lines = []
                        self.code_language = ''
                        # Remove processed content from buffer
                        self.buffer = '\n'.join(lines[lines.index(line)+1:])
                        break
                    else:
                        # Accumulate code line
                        if line or self.code_lines:  # Don't add first empty line
                            self.code_lines.append(line)
            return
        
        # If we're in a table, accumulate until non-table line
        if self.in_table:
            if '\n' in self.buffer:
                lines = self.buffer.split('\n')
                for i, line in enumerate(lines):
                    stripped = line.rstrip()
                    table_row = self.parser.parse_table_row(stripped)
                    if table_row is not None:
                        # Only append non-empty rows (skip separator rows)
                        if table_row:  # Not an empty list
                            self.table_rows.append(table_row)
                        # Empty list means separator row - continue table
                    else:
                        # End of table
                        if self.table_rows:
                            formatted = self.formatter.format_table(self.table_rows)
                            self._write(formatted)
                        self.in_table = False
                        self.table_rows = []
                        # Process remaining lines
                        self.buffer = '\n'.join(lines[i:])
                        break
                else:
                    # All lines were table rows
                    self.buffer = ''
                    return
        
        # Process complete lines for regular markdown
        while '\n' in self.buffer:
            line, self.buffer = self.buffer.split('\n', 1)
            self._process_line(line + '\n')
        
        # Don't process remaining buffer - wait for more content
    
    def _is_incomplete(self):
        """Check if buffer contains incomplete markdown syntax"""
        # Check for incomplete code fence
        if self.buffer.strip().startswith('`'):
            return True
        
        # Check for incomplete inline code
        if self.buffer.count('`') % 2 == 1:
            return True
        
        # Check for incomplete link/bold/italic
        if any(self.buffer.endswith(c) for c in ['[', '(', '*', '_']):
            return True
        
        return False
    
    def _process_line(self, line):
        """Process a single line of markdown"""
        stripped = line.rstrip()
        
        # Code block handling
        lang = self.parser.parse_code_block_delimiter(stripped)
        if lang is not None:
            if not self.in_code_block:
                # Start of code block
                self.in_code_block = True
                self.code_language = lang
                self.code_lines = []
            return
        
        if self.in_code_block:
            # This shouldn't happen with new logic, but keep for safety
            self.code_lines.append(line.rstrip('\n'))
            return
        
        # Table handling
        table_row = self.parser.parse_table_row(stripped)
        if table_row is not None:
            if not self.in_table:
                self.in_table = True
                self.table_rows = []
            self.table_rows.append(table_row)
            return
        elif self.in_table:
            # End of table
            formatted = self.formatter.format_table(self.table_rows)
            self._write(formatted)
            self.in_table = False
            self.table_rows = []
            # Continue processing this line
        
        # Blockquote handling
        blockquote_text = self.parser.parse_blockquote(stripped)
        if blockquote_text is not None:
            if not self.in_blockquote:
                self.in_blockquote = True
                self.blockquote_lines = []
            self.blockquote_lines.append(blockquote_text)
            return
        elif self.in_blockquote:
            # End of blockquote
            text = '\n'.join(self.blockquote_lines)
            formatted = self.formatter.format_blockquote(text)
            self._write(formatted)
            self.in_blockquote = False
            self.blockquote_lines = []
            # Continue processing this line
        
        # Horizontal rule
        if self.parser.is_hr(stripped):
            self._write(self.formatter.format_hr())
            return
        
        # Heading
        heading = self.parser.parse_heading(stripped)
        if heading:
            level, text = heading
            text = self.parser.apply_inline_formatting(text, self.formatter)
            formatted = self.formatter.format_heading(level, text)
            self._write(formatted)
            return
        
        # Checkbox
        checkbox = self.parser.parse_checkbox(stripped)
        if checkbox:
            checked, text = checkbox
            text = self.parser.apply_inline_formatting(text, self.formatter)
            formatted = self.formatter.format_checkbox(checked, text)
            self._write(formatted + '\n')
            return
        
        # Ordered list
        ordered_item = self.parser.parse_ordered_list_item(stripped)
        if ordered_item:
            indent, number, text = ordered_item
            text = self.parser.apply_inline_formatting(text, self.formatter)
            formatted = self.formatter.format_list_item(text, ordered=True, number=number, indent_level=indent)
            self._write(formatted + '\n')
            return
        
        # Unordered list
        list_item = self.parser.parse_list_item(stripped)
        if list_item:
            indent, text = list_item
            text = self.parser.apply_inline_formatting(text, self.formatter)
            formatted = self.formatter.format_list_item(text, ordered=False, indent_level=indent)
            self._write(formatted + '\n')
            return
        
        # Regular text with inline formatting
        if stripped:
            formatted = self.parser.apply_inline_formatting(line, self.formatter)
            self._write(formatted)
        else:
            self._write(line)
    
    def finalize(self):
        """
        Finalize rendering, flushing any remaining buffered content
        Call this after all chunks have been rendered
        """
        # Process remaining buffer
        if self.buffer:
            self._process_line(self.buffer)
            self.buffer = ''
        
        # Flush any incomplete blocks
        if self.in_code_block and self.code_lines:
            code = '\n'.join(self.code_lines)
            formatted = self.formatter.format_code_block(
                code,
                self.code_language,
                self.line_numbers
            )
            self._write(formatted)
            self.in_code_block = False
            self.code_lines = []
        
        if self.in_table and self.table_rows:
            formatted = self.formatter.format_table(self.table_rows)
            self._write(formatted)
            self.in_table = False
            self.table_rows = []
        
        if self.in_blockquote and self.blockquote_lines:
            text = '\n'.join(self.blockquote_lines)
            formatted = self.formatter.format_blockquote(text)
            self._write(formatted)
            self.in_blockquote = False
            self.blockquote_lines = []
        
        # Flush output
        self.output.flush()
    
    def _write(self, text):
        """Write text to output"""
        self.output.write(text)
        self.output.flush()
