"""
Main markdown renderer for streaming LLM responses
"""

import sys
import re
from .parser import MarkdownParser
from .formatters import MarkdownFormatter
from .themes import get_theme
from .colors import get_terminal_width, colorize, Colors


class RenderState:
    """Tracks rendering state for streaming content"""
    def __init__(self):
        self.in_code_block = False
        self.code_language = ''
        self.code_lines = []
        self.code_line_count = 0
        self.in_table = False
        self.table_rows = []
        self.table_row_count = 0
        self.in_blockquote = False
        self.blockquote_lines = []
        self.alert_type = None

    def reset_code(self):
        self.in_code_block = False
        self.code_language = ''
        self.code_lines = []
        self.code_line_count = 0

    def reset_table(self):
        self.in_table = False
        self.table_rows = []
        self.table_row_count = 0

    def reset_blockquote(self):
        self.in_blockquote = False
        self.blockquote_lines = []
        self.alert_type = None

    def reset_all(self):
        self.reset_code()
        self.reset_table()
        self.reset_blockquote()


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
            stream_code: Render code lines as they arrive (default: True)
                         When False, buffers entire code block until closing fence
        """
        self.theme_config = get_theme(theme)
        self.code_background = code_background
        self.line_numbers = line_numbers
        self.stream_code = stream_code
        self.width = width or get_terminal_width()
        self.output = output or self._get_utf8_output(sys.stdout)

        self.parser = MarkdownParser()
        self.formatter = MarkdownFormatter(
            self.theme_config,
            inline_code_color=inline_code_color,
            code_background=code_background,
            width=self.width
        )

        self.buffer = ''
        self.state = RenderState()
        self._last_element = None
        self._last_output_ended_with_newline = False

    def render(self, chunk):
        """
        Render a chunk of markdown content

        Args:
            chunk: Markdown text chunk from streaming response
        """
        if not chunk:
            return

        self.buffer += chunk

        if self.state.in_code_block:
            self._handle_code_block_buffer()
            return

        if self.state.in_table:
            self._handle_table_buffer()
            if self.state.in_table:
                return

        while '\n' in self.buffer:
            line, self.buffer = self.buffer.split('\n', 1)
            self._process_line(line + '\n')

    def _handle_code_block_buffer(self):
        if '\n' not in self.buffer:
            return

        lines = self.buffer.split('\n')
        has_trailing_newline = lines and lines[-1] == ''
        if has_trailing_newline:
            lines = lines[:-1]

        closing_idx = -1
        for idx, line in enumerate(lines):
            if line.strip().startswith('```'):
                closing_idx = idx
                break

        if closing_idx >= 0:
            new_lines = lines[:closing_idx]
            if self.stream_code:
                for l in new_lines:
                    if l == '' and not self.state.code_lines:
                        continue
                    self.state.code_line_count += 1
                    self.state.code_lines.append(l)
                    self._write_code_line(l)
            else:
                code_lines = [l for l in new_lines if l != '' or self.state.code_lines]
                all_code = '\n'.join(self.state.code_lines + code_lines)
                formatted = self.formatter.format_code_block(
                    all_code,
                    self.state.code_language,
                    self.line_numbers
                )
                self._write(formatted, 'code_block')
            self.state.reset_code()
            remaining_lines = lines[closing_idx + 1:]
            suffix = '\n' if has_trailing_newline else ''
            self.buffer = '\n'.join(remaining_lines) + suffix
            if remaining_lines or has_trailing_newline:
                self.render('')
        else:
            if self.stream_code:
                for l in lines:
                    if l == '' and not self.state.code_lines:
                        continue
                    self.state.code_line_count += 1
                    self.state.code_lines.append(l)
                    self._write_code_line(l)
                self.buffer = ''
            else:
                code_lines = [l for l in lines if l != '' or self.state.code_lines]
                self.state.code_lines.extend(code_lines)
                self.buffer = ''

    def _handle_table_buffer(self):
        """Process buffer when inside a table"""
        if '\n' not in self.buffer:
            return

        lines = self.buffer.split('\n')
        if lines and lines[-1] == '':
            lines = lines[:-1]
            has_trailing_newline = True
        else:
            has_trailing_newline = False

        for i, line in enumerate(lines):
            stripped = line.rstrip()
            table_row = self.parser.parse_table_row(stripped)
            if table_row is not None:
                self.state.table_row_count += 1
                if not (self.state.table_row_count == 2 and self.parser.is_separator_row(table_row)):
                    formatted_row = [self.parser.apply_inline_formatting(cell, self.formatter) for cell in table_row]
                    self.state.table_rows.append(formatted_row)
            else:
                if self.state.table_rows:
                    formatted = self.formatter.format_table(self.state.table_rows)
                    self._write(formatted, 'table')
                self.state.reset_table()
                remaining = lines[i:]
                if has_trailing_newline:
                    remaining.append('')
                self.buffer = '\n'.join(remaining)
                return

        self.buffer = ''

    def _process_line(self, line):
        """Process a single line of markdown"""
        stripped = line.rstrip()

        lang = self.parser.parse_code_block_delimiter(stripped)
        if lang is not None:
            if not self.state.in_code_block:
                self.state.in_code_block = True
                self.state.code_language = lang
                self.state.code_lines = []
                self.state.code_line_count = 0
            else:
                if not self.stream_code:
                    code = '\n'.join(self.state.code_lines)
                    formatted = self.formatter.format_code_block(
                        code,
                        self.state.code_language,
                        self.line_numbers
                    )
                    self._write(formatted, 'code_block')
                self.state.reset_code()
            return

        if self.state.in_code_block:
            content = line.rstrip('\n')
            self.state.code_lines.append(content)
            if self.stream_code:
                self.state.code_line_count += 1
                self._write_code_line(content)
            return

        table_row = self.parser.parse_table_row(stripped)
        if table_row is not None:
            if not self.state.in_table:
                self.state.in_table = True
                self.state.table_rows = []
                self.state.table_row_count = 0
            self.state.table_row_count += 1
            if not (self.state.table_row_count == 2 and self.parser.is_separator_row(table_row)):
                formatted_row = [self.parser.apply_inline_formatting(cell, self.formatter) for cell in table_row]
                self.state.table_rows.append(formatted_row)
            return
        elif self.state.in_table:
            formatted = self.formatter.format_table(self.state.table_rows)
            self._write(formatted, 'table')
            self.state.reset_table()

        blockquote_text = self.parser.parse_blockquote(stripped)
        if blockquote_text is not None:
            if not self.state.in_blockquote:
                self.state.in_blockquote = True
                self.state.blockquote_lines = []
                self.state.alert_type = self.parser.parse_alert(stripped)
                if self.state.alert_type:
                    return
            self.state.blockquote_lines.append(blockquote_text)
            return
        elif self.state.in_blockquote:
            text = '\n'.join(self.state.blockquote_lines)
            if self.state.alert_type:
                formatted = self.formatter.format_alert(self.state.alert_type, text)
            elif text:
                formatted = self.formatter.format_blockquote(text)
            else:
                formatted = ''
            if formatted:
                self._write(formatted, 'blockquote')
            self.state.reset_blockquote()

        if self.parser.is_hr(stripped):
            self._write(self.formatter.format_hr(), 'hr')
            return

        heading = self.parser.parse_heading(stripped)
        if heading:
            level, text = heading
            text = self.parser.apply_inline_formatting(text, self.formatter)
            formatted = self.formatter.format_heading(level, text)
            self._write(formatted, 'heading')
            return

        checkbox = self.parser.parse_checkbox(stripped)
        if checkbox:
            checked, text = checkbox
            text = self.parser.apply_inline_formatting(text, self.formatter)
            formatted = self.formatter.format_checkbox(checked, text)
            self._write(formatted + '\n', 'checkbox')
            return

        ordered_item = self.parser.parse_ordered_list_item(stripped)
        if ordered_item:
            indent, number, text = ordered_item
            text = self.parser.apply_inline_formatting(text, self.formatter)
            formatted = self.formatter.format_list_item(text, ordered=True, number=number, indent_level=indent)
            self._write(formatted + '\n', 'ordered_list')
            return

        list_item = self.parser.parse_list_item(stripped)
        if list_item:
            indent, text = list_item
            text = self.parser.apply_inline_formatting(text, self.formatter)
            formatted = self.formatter.format_list_item(text, ordered=False, indent_level=indent)
            self._write(formatted + '\n', 'list_item')
            return

        if stripped:
            formatted = self.parser.apply_inline_formatting(line, self.formatter)
            self._write(formatted, 'inline')
        else:
            self._write(line, 'inline')

    def finalize(self):
        """
        Finalize rendering, flushing any remaining buffered content
        Call this after all chunks have been rendered
        """
        if self.buffer:
            self._process_line(self.buffer)
            self.buffer = ''

        if self.state.in_code_block:
            if not self.stream_code:
                code = '\n'.join(self.state.code_lines)
                formatted = self.formatter.format_code_block(
                    code,
                    self.state.code_language,
                    self.line_numbers
                )
                self._write(formatted, 'code_block')
            self.state.reset_code()

        if self.state.in_table and self.state.table_rows:
            formatted = self.formatter.format_table(self.state.table_rows)
            self._write(formatted, 'table')
            self.state.reset_table()

        if self.state.in_blockquote:
            text = '\n'.join(self.state.blockquote_lines)
            if self.state.alert_type:
                formatted = self.formatter.format_alert(self.state.alert_type, text)
            elif text:
                formatted = self.formatter.format_blockquote(text)
            else:
                formatted = ''
            if formatted:
                self._write(formatted, 'blockquote')
            self.state.reset_blockquote()

        self.output.flush()

    @staticmethod
    def _get_utf8_output(stream):
        """Ensure output stream can handle UTF-8 characters"""
        if hasattr(stream, 'reconfigure'):
            try:
                stream.reconfigure(encoding='utf-8', errors='replace')
            except Exception:
                pass
        return stream

    def _ensure_spacing(self, element_type):
        """Ensure proper spacing before writing a block-level element"""
        if element_type == 'inline':
            return
        is_list = element_type in ('list_item', 'checkbox', 'ordered_list')
        if is_list and self._last_element in ('list_item', 'checkbox', 'ordered_list', None):
            return
        is_code_stream = element_type == 'code_block' and self._last_element == 'code_block'
        if is_code_stream:
            return
        if self._last_element is not None and self._last_element != 'inline':
            self.output.write('\n')
        self._last_element = element_type

    def _write(self, text, element_type='inline'):
        """Write text to output with spacing management"""
        self._ensure_spacing(element_type)
        try:
            self.output.write(text)
        except UnicodeEncodeError:
            self.output.write(text.encode('utf-8', errors='replace').decode('utf-8'))
        self.output.flush()
        self._last_output_ended_with_newline = text.endswith('\n')

    def _write_code_line(self, line):
        """Write a single code line during streaming with per-line highlighting"""
        highlighted = self.formatter.format_code_line(line, self.state.code_language)
        if self.line_numbers:
            num = self.state.code_line_count
            formatted = colorize(f'{num:>4}', Colors.BRIGHT_BLACK)
            self._write(f' {formatted}  {highlighted}\n', 'code_block')
        else:
            self._write(f'  {highlighted}\n', 'code_block')
