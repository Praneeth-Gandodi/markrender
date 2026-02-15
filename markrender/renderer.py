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
        force_color=False,
        stream_code=True
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
            stream_code: Stream code blocks line by line (default: True). If False, render the whole block at once.
        """
        self.theme_config = get_theme(theme)
        self.code_background = code_background
        self.line_numbers = line_numbers
        self.width = width or get_terminal_width()
        self.output = output or sys.stdout
        self.force_color = force_color
        self.stream_code = stream_code
        
        # Initialize parser and formatter
        self.parser = MarkdownParser()
        self.formatter = MarkdownFormatter(
            self.theme_config,
            inline_code_color=inline_code_color,
            code_background=code_background,
            width=self.width,
            force_color=self.force_color,
            output=output
        )
        
        # Buffer for incomplete content
        self.buffer = ''
        
        # State tracking
        self.in_code_block = False
        self.code_language = ''
        self.code_buffer = []
        self.in_table = False
        self.table_buffer = []
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
        
        # Add to buffer and process
        self.buffer += chunk
        self._process_buffer()

    def _process_buffer(self):
        """Processes the buffer to find and format complete markdown elements."""
        while '\n' in self.buffer or (self.finalizing and self.buffer):
            if '\n' in self.buffer:
                line, self.buffer = self.buffer.split('\n', 1)
            else:
                line = self.buffer
                self.buffer = ''
            self._process_line(line)
    
    def _flush_table(self):
        """Flushes the buffered table rows and resets table state."""
        if not self.table_buffer:
            self.in_table = False
            self.table_buffer = []
            return

        # A valid GFM table needs at least a header and a separator
        if len(self.table_buffer) < 2:
            # Not enough lines for a valid table, treat as regular paragraphs
            for line in self.table_buffer:
                self.paragraph_buffer.append(line)
            self._flush_paragraph_buffer()
            self.in_table = False
            self.table_buffer = []
            return
        
        header_line = self.table_buffer[0]
        separator_line = self.table_buffer[1]
        
        header = self.parser.parse_table_row(header_line)
        parsed_separator = self.parser.parse_table_row(separator_line)

        # A valid separator must parse to an empty list and exist
        if not header or parsed_separator != []:
            # The second line is not a valid separator, treat all buffered lines as paragraphs
            for line in self.table_buffer:
                self.paragraph_buffer.append(line)
            self._flush_paragraph_buffer()
            self.in_table = False
            self.table_buffer = []
            return

        data_rows = []
        for row_line in self.table_buffer[2:]: # Data rows start from the third line
            row = self.parser.parse_table_row(row_line)
            if row is not None: # Ensure it's a valid table row, not just arbitrary text
                data_rows.append(row)
            else:
                # If a non-table row is encountered mid-table, flush the table and then buffer the non-table line
                self._write(self.formatter.format_table(
                    [self.parser.apply_inline_formatting(cell, self.formatter) for cell in header],
                    [[self.parser.apply_inline_formatting(cell, self.formatter) for cell in r] for r in self._validate_data_rows(header, data_rows)]
                ))
                self.in_table = False
                self.table_buffer = []
                self._process_line(row_line) # Re-process the current non-table line
                return
        
        # All lines processed, flush the table
        self._write(self.formatter.format_table(
            [self.parser.apply_inline_formatting(cell, self.formatter) for cell in header],
            [[self.parser.apply_inline_formatting(cell, self.formatter) for cell in r] for r in self._validate_data_rows(header, data_rows)]
        ))
        
        self.in_table = False
        self.table_buffer = []

    def _validate_data_rows(self, header, data_rows):
        """Helper to ensure data rows match header column count."""
        num_cols = len(header)
        validated_rows = []
        for row in data_rows:
            if len(row) < num_cols:
                validated_rows.append(row + [''] * (num_cols - len(row)))
            elif len(row) > num_cols:
                validated_rows.append(row[:num_cols])
            else:
                validated_rows.append(row)
        return validated_rows

    def _process_line(self, line):
        """Process a single line of markdown"""
        stripped = line.rstrip()

        # If the line is a block-level element, flush the paragraph buffer.
        is_block = (
            self.parser.is_hr(stripped) or
            self.parser.parse_heading(stripped) or
            self.parser.parse_code_block_delimiter(stripped) is not None or
            self.parser.parse_table_row(stripped) is not None or # This needs to be robust for detecting *start* of table
            self.parser.BLOCKQUOTE_PATTERN.match(line) or
            self.parser.parse_checkbox(stripped) or
            self.parser.parse_ordered_list_item(stripped) or
            self.parser.parse_list_item(stripped)
        )

        if is_block and not self.in_table:
            self._flush_paragraph_buffer()

        # Code block handling
        if self.in_code_block:
            if self.parser.parse_code_block_delimiter(stripped) is not None:
                if not self.stream_code:
                    code = '\n'.join(self.code_buffer)
                    formatted = self.formatter.format_code_block(code, self.code_language, self.line_numbers)
                    self._write(formatted)
                else:
                    self._write(self.formatter.end_code_block(self.code_language))
                self.in_code_block = False
                self.code_language = ''
                self.code_buffer = []
            else:
                if self.stream_code:
                    self._write(self.formatter.stream_code_line(line, self.code_language, self.line_numbers))
                else:
                    self.code_buffer.append(line)
            return

        lang = self.parser.parse_code_block_delimiter(stripped)
        if lang is not None:
            if not self.in_code_block:
                if self.in_table:
                    self._flush_table()
                self.in_code_block = True
                self.code_language = lang
                if self.stream_code:
                    self._write(self.formatter.start_code_block(self.code_language, self.line_numbers))
            return

        # Table handling
        table_row_parsed = self.parser.parse_table_row(stripped)
        
        if table_row_parsed is not None:
            # If current line is a table row
            if not self.in_table:
                # If not currently in a table, start one
                self.in_table = True
            self.table_buffer.append(stripped)
            return
        elif self.in_table:
            # If currently in a table AND current line is NOT a table row,
            # then the table has ended. Flush the buffered table and then
            # process the current (non-table) line.
            self._flush_table()
            # After flushing, we are no longer in a table state.
            # Now, process the current line as a new element.
            self._process_line(line)
            return # Ensure no further processing of this line in the current call


        # Blockquote handling
        # Parse blockquote using the new parser method which returns (text, level)
        blockquote_data = self.parser.parse_blockquote(line)
        if blockquote_data:
            blockquote_text, nesting_level = blockquote_data
            
            if self.in_table:
                self._flush_table()
                
            if not self.in_blockquote:
                self.in_blockquote = True
                self.blockquote_lines = []
            
            self.blockquote_lines.append((blockquote_text.strip(), nesting_level))
            return
        elif self.in_blockquote:
            # The blockquote has ended, so we need to format and print it.
            formatted = self.formatter.format_blockquote(self.blockquote_lines)
            self._write(formatted + '\n')
            self.in_blockquote = False
            self.blockquote_lines = []
            # After flushing the blockquote, process the current line
            self._process_line(line)
            return

        # Horizontal rule
        if self.parser.is_hr(stripped):
            if self.in_table:
                self._flush_table()
            self._write(self.formatter.format_hr())
            return
        
        # Heading
        heading = self.parser.parse_heading(stripped)
        if heading:
            if self.in_table:
                self._flush_table()
            level, text = heading
            text = self.parser.apply_inline_formatting(text, self.formatter)
            formatted = self.formatter.format_heading(level, text)
            self._write(formatted)
            return
        
        # Checkbox
        checkbox = self.parser.parse_checkbox(stripped)
        if checkbox:
            if self.in_table:
                self._flush_table()
            checked, text = checkbox
            text = self.parser.apply_inline_formatting(text, self.formatter)
            formatted = self.formatter.format_checkbox(checked, text)
            self._write(formatted + '\n')
            return
        
        # Ordered list
        ordered_item = self.parser.parse_ordered_list_item(stripped)
        if ordered_item:
            if self.in_table:
                self._flush_table()
            indent, number, text = ordered_item
            text = self.parser.apply_inline_formatting(text, self.formatter)
            formatted = self.formatter.format_list_item(text, ordered=True, number=number, indent_level=indent)
            self._write(formatted + '\n')
            return
        
        # Unordered list
        list_item = self.parser.parse_list_item(stripped)
        if list_item:
            if self.in_table:
                self._flush_table()
            indent, text = list_item
            text = self.parser.apply_inline_formatting(text, self.formatter)
            formatted = self.formatter.format_list_item(text, ordered=False, indent_level=indent)
            self._write(formatted + '\n')
            return
        
        # Regular text
        if stripped:
            if self.in_table:
                self._flush_table()
            self.paragraph_buffer.append(stripped)
        else:
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
            self._process_buffer()

        # Flush any incomplete blocks
        self._flush_paragraph_buffer()

        
        if self.in_table: # If a table is still open, flush it
            self._flush_table()
        
        if self.in_blockquote and self.blockquote_lines:
            formatted = self.formatter.format_blockquote(self.blockquote_lines)
            self._write(formatted + '\n')
            self.in_blockquote = False
            self.blockquote_lines = []
        
        # Flush output
        self.output.flush()
        self.finalizing = False
    
    def _write(self, text):
        """Write text to output"""
        # Always use rich console to print, so markup is rendered
        if self.formatter.console:
            # Print directly to the console which handles the output
            self.formatter.console.print(text, end='')
        else:
            # Fallback if rich is not available
            self.output.write(str(text))
        self.output.flush()
