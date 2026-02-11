"""
Main markdown renderer for streaming LLM responses
"""

import sys
import re
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
        output=None,
        force_color=False
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
            force_color: Force color output even if terminal does not support it (default: False)
        """
        self.theme_config = get_theme(theme)
        self.code_background = code_background
        self.line_numbers = line_numbers
        self.width = width or get_terminal_width()
        self.output = output or sys.stdout
        self.force_color = force_color
        
        # Initialize parser and formatter
        self.parser = MarkdownParser()
        self.formatter = MarkdownFormatter(
            self.theme_config,
            inline_code_color=inline_code_color,
            code_background=code_background,
            width=self.width,
            force_color=self.force_color
        )
        
        # Buffer for incomplete content
        self.buffer = ''
        
        # State tracking
        self.in_code_block = False
        self.code_language = ''
        self.code_lines = []
        self.in_table = False
        self.table_header = None        # Stores the header row
        self.table_data_rows = []       # Stores list of data rows
        self.in_blockquote = False
        self.blockquote_lines = []
        self.paragraph_buffer = []
        self.finalizing = False
    
    def _flush_paragraph_buffer(self):
        if self.paragraph_buffer:
            paragraph = ' '.join(self.paragraph_buffer)
            # If there's incomplete inline formatting and we are not in the finalizing stage,
            # do not flush the paragraph yet.
            if not self.finalizing and self.parser.is_inline_incomplete(paragraph):
                return
            
            formatted = self.parser.apply_inline_formatting(paragraph, self.formatter)
            self._write(formatted + '\n\n')
            self.paragraph_buffer = []

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
        
        # Process all full lines
        while '\n' in self.buffer:
            line, self.buffer = self.buffer.split('\n', 1)
            self._process_line(line)

    def _flush_table(self):
        """Flushes the buffered table rows and resets table state."""
        if self.in_table and self.table_header is not None:
            # Perform column validation before formatting (Issue 3)
            # Pad shorter rows with empty strings to match header column count
            num_cols = len(self.table_header)
            validated_data_rows = []
            for row in self.table_data_rows:
                if len(row) < num_cols:
                    validated_data_rows.append(row + [''] * (num_cols - len(row)))
                elif len(row) > num_cols:
                    validated_data_rows.append(row[:num_cols]) # Truncate if too many columns
                else:
                    validated_data_rows.append(row)

            # Apply inline formatting to header and data cells (Issue 4)
            formatted_header = [
                self.parser.apply_inline_formatting(cell, self.formatter) for cell in self.table_header
            ]
            formatted_data_rows = [
                [self.parser.apply_inline_formatting(cell, self.formatter) for cell in row]
                for row in validated_data_rows
            ]
            formatted = self.formatter.format_table(formatted_header, formatted_data_rows)
            self._write(formatted)
        
        self.in_table = False
        self.table_header = None
        self.table_data_rows = []

    def _process_line(self, line):
        """Process a single line of markdown"""
        stripped = line.rstrip()

        # Code block handling
        if self.in_code_block:
            if self.parser.parse_code_block_delimiter(stripped) is not None:
                # End of code block
                self._flush_paragraph_buffer()
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
            else:
                self.code_lines.append(line) # Keep original line with spaces
            return

        lang = self.parser.parse_code_block_delimiter(stripped)
        if lang is not None:
            if not self.in_code_block:
                # Start of code block
                self._flush_paragraph_buffer()
                if self.in_table: # If a code block starts, flush any pending table
                    self._flush_table()
                self.in_code_block = True
                self.code_language = lang
                self.code_lines = []
            return
        
        # Table handling
        table_row = self.parser.parse_table_row(stripped)
        if table_row is not None:
            self._flush_paragraph_buffer()
            if not self.in_table:
                self.in_table = True
                self.table_header = None
                self.table_data_rows = []
            
            # If it's a separator row, just acknowledge it.
            # The parser returns [] for separator rows.
            if table_row == []:
                # If we haven't seen a header yet, this separator is invalid, ignore it.
                # Or if we already have a header and this is the separator.
                pass 
            elif self.table_header is None:
                # This is the first non-separator row, assume it's the header
                self.table_header = table_row
            else:
                # This is a data row
                self.table_data_rows.append(table_row)
            return
        elif self.in_table:
            # End of table: a non-table line was encountered
            self._flush_paragraph_buffer()
            self._flush_table()
            # Continue processing this line as it might be other markdown
        
        # Blockquote handling
        blockquote_match = self.parser.BLOCKQUOTE_PATTERN.match(line)
        if blockquote_match:
            self._flush_paragraph_buffer()
            if self.in_table: # If a blockquote starts, flush any pending table
                self._flush_table()
            blockquote_text = blockquote_match.group(2)
            nesting_level = len(blockquote_match.group(1)) // 2
            if not self.in_blockquote:
                self.in_blockquote = True
                self.blockquote_lines = []
            self.blockquote_lines.append((blockquote_text.strip(), nesting_level))
            return
        elif self.in_blockquote:
            # End of blockquote
            self._flush_paragraph_buffer()
            text = '\n'.join([line for line, _ in self.blockquote_lines])
            # Assuming same nesting level for the whole block for simplicity
            nesting_level = self.blockquote_lines[0][1] if self.blockquote_lines else 0
            formatted = self.formatter.format_blockquote(text, nesting_level)
            self._write(formatted + '\n')
            self.in_blockquote = False
            self.blockquote_lines = []

        # Horizontal rule
        if self.parser.is_hr(stripped):
            self._flush_paragraph_buffer()
            if self.in_table: # If a HR starts, flush any pending table
                self._flush_table()
            self._write(self.formatter.format_hr())
            return
        
        # Heading
        heading = self.parser.parse_heading(stripped)
        if heading:
            self._flush_paragraph_buffer()
            if self.in_table: # If a heading starts, flush any pending table
                self._flush_table()
            level, text = heading
            text = self.parser.apply_inline_formatting(text, self.formatter)
            formatted = self.formatter.format_heading(level, text)
            self._write(formatted)
            return
        
        # Checkbox
        checkbox = self.parser.parse_checkbox(stripped)
        if checkbox:
            self._flush_paragraph_buffer()
            if self.in_table: # If a checkbox starts, flush any pending table
                self._flush_table()
            checked, text = checkbox
            text = self.parser.apply_inline_formatting(text, self.formatter)
            formatted = self.formatter.format_checkbox(checked, text)
            self._write(formatted + '\n')
            return
        
        # Ordered list
        ordered_item = self.parser.parse_ordered_list_item(stripped)
        if ordered_item:
            self._flush_paragraph_buffer()
            if self.in_table: # If a list starts, flush any pending table
                self._flush_table()
            indent, number, text = ordered_item
            text = self.parser.apply_inline_formatting(text, self.formatter)
            formatted = self.formatter.format_list_item(text, ordered=True, number=number, indent_level=indent)
            self._write(formatted + '\n')
            return
        
        # Unordered list
        list_item = self.parser.parse_list_item(stripped)
        if list_item:
            self._flush_paragraph_buffer()
            if self.in_table: # If a list starts, flush any pending table
                self._flush_table()
            indent, text = list_item
            text = self.parser.apply_inline_formatting(text, self.formatter)
            formatted = self.formatter.format_list_item(text, ordered=False, indent_level=indent)
            self._write(formatted + '\n')
            return
        
        # Regular text with inline formatting
        if stripped:
            if self.in_table: # If regular text after separator, flush table.
                self._flush_table()
            self.paragraph_buffer.append(stripped)
        else:
            # Empty line, flush table if in table
            if self.in_table:
                self._flush_table()
            self._flush_paragraph_buffer()
    
    def finalize(self):
        """
        Finalize rendering, flushing any remaining buffered content
        Call this after all chunks have been rendered
        """
        self.finalizing = True
        # Process remaining buffer
        if self.buffer:
            self._process_line(self.buffer)
            self.buffer = ''
        
        # Flush any incomplete blocks
        self._flush_paragraph_buffer()

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
        
        if self.in_table: # If a table is still open, flush it
            self._flush_table()
        
        if self.in_blockquote and self.blockquote_lines:
            text = '\n'.join([line for line, _ in self.blockquote_lines])
            nesting_level = self.blockquote_lines[0][1] if self.blockquote_lines else 0
            formatted = self.formatter.format_blockquote(text, nesting_level)
            self._write(formatted + '\n')
            self.in_blockquote = False
            self.blockquote_lines = []
        
        # Flush output
        self.output.flush()
        self.finalizing = False
    
    def _write(self, text):
        """Write text to output"""
        self.output.write(text)
        self.output.flush()
