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
        self.paragraph_buffer = []
    
    def _flush_paragraph_buffer(self):
        if self.paragraph_buffer:
            paragraph = ' '.join(self.paragraph_buffer)
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
                self.in_code_block = True
                self.code_language = lang
                self.code_lines = []
            return
        
        # Flush paragraph if table starts
        table_row = self.parser.parse_table_row(stripped)
        if table_row is not None:
            self._flush_paragraph_buffer()
            if not self.in_table:
                self.in_table = True
                self.table_rows = []
            
            # Sanitize row: remove empty strings from start/end
            if table_row and not table_row[0]:
                table_row.pop(0)
            if table_row and not table_row[-1]:
                table_row.pop(-1)

            # Apply inline formatting to each cell
            formatted_row = [self.parser.apply_inline_formatting(cell, self.formatter) for cell in table_row]
                
            self.table_rows.append(formatted_row)
            return
        elif self.in_table:
            # End of table
            self._flush_paragraph_buffer()
            formatted = self.formatter.format_table(self.table_rows)
            self._write(formatted)
            self.in_table = False
            self.table_rows = []
            # Continue processing this line
        
        # Blockquote handling
        blockquote_match = self.parser.BLOCKQUOTE_PATTERN.match(line)
        if blockquote_match:
            self._flush_paragraph_buffer()
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
            self._write(self.formatter.format_hr())
            return
        
        # Heading
        heading = self.parser.parse_heading(stripped)
        if heading:
            self._flush_paragraph_buffer()
            level, text = heading
            text = self.parser.apply_inline_formatting(text, self.formatter)
            formatted = self.formatter.format_heading(level, text)
            self._write(formatted)
            return
        
        # Checkbox
        checkbox = self.parser.parse_checkbox(stripped)
        if checkbox:
            self._flush_paragraph_buffer()
            checked, text = checkbox
            text = self.parser.apply_inline_formatting(text, self.formatter)
            formatted = self.formatter.format_checkbox(checked, text)
            self._write(formatted + '\n')
            return
        
        # Ordered list
        ordered_item = self.parser.parse_ordered_list_item(stripped)
        if ordered_item:
            self._flush_paragraph_buffer()
            indent, number, text = ordered_item
            text = self.parser.apply_inline_formatting(text, self.formatter)
            formatted = self.formatter.format_list_item(text, ordered=True, number=number, indent_level=indent)
            self._write(formatted + '\n')
            return
        
        # Unordered list
        list_item = self.parser.parse_list_item(stripped)
        if list_item:
            self._flush_paragraph_buffer()
            indent, text = list_item
            text = self.parser.apply_inline_formatting(text, self.formatter)
            formatted = self.formatter.format_list_item(text, ordered=False, indent_level=indent)
            self._write(formatted + '\n')
            return
        
        # Regular text with inline formatting
        if stripped:
            self.paragraph_buffer.append(stripped)
        else:
            self._flush_paragraph_buffer()
    
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
        
        if self.in_table and self.table_rows:
            formatted = self.formatter.format_table(self.table_rows)
            self._write(formatted)
            self.in_table = False
            self.table_rows = []
        
        if self.in_blockquote and self.blockquote_lines:
            text = '\n'.join([line for line, _ in self.blockquote_lines])
            nesting_level = self.blockquote_lines[0][1] if self.blockquote_lines else 0
            formatted = self.formatter.format_blockquote(text, nesting_level)
            self._write(formatted + '\n')
            self.in_blockquote = False
            self.blockquote_lines = []
        
        # Flush output
        self.output.flush()
    
    def _write(self, text):
        """Write text to output"""
        self.output.write(text)
        self.output.flush()
