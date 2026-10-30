"""
Main markdown renderer for streaming LLM responses
"""

import sys
from typing import Optional
from .parser import MarkdownParser
from .formatters import MarkdownFormatter
from .themes import get_theme
from .config import RendererConfig
from .colors import get_terminal_width, colorize, Colors, strip_ansi, dim_text


class RenderState:
    """Tracks rendering state for streaming content"""
    def __init__(self):
        self.in_code_block = False
        self.code_language = ''
        self.code_fence_length = 3
        self.code_lines = []
        self.code_line_count = 0
        self.code_line_num_width = 3
        self.in_table = False
        self.table_rows = []
        self.table_row_count = 0
        self.table_alignments = []
        self.in_blockquote = False
        self.blockquote_lines = []
        self.alert_type: Optional[str] = None

    def reset_code(self):
        self.in_code_block = False
        self.code_language = ''
        self.code_fence_length = 3
        self.code_lines = []
        self.code_line_count = 0

    def reset_table(self):
        self.in_table = False
        self.table_rows = []
        self.table_row_count = 0
        self.table_alignments = []

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
        theme=None,
        code_background=None,
        inline_code_color=None,
        line_numbers=None,
        width=None,
        output=None,
        stream_code=None,
        force_color=None,
        use_config=True,
        config=None,
    ):
        if config is None:
            config = RendererConfig.from_file() if use_config else RendererConfig()
        explicit = {
            'theme': theme,
            'code_background': code_background,
            'inline_code_color': inline_code_color,
            'line_numbers': line_numbers,
            'width': width,
            'stream_code': stream_code,
            'force_color': force_color,
        }
        for key, value in explicit.items():
            if value is not None:
                config.config[key] = value

        self.theme_config = get_theme(config.theme)
        self.code_background = config.code_background
        self.line_numbers = config.line_numbers
        self.stream_code = config.stream_code
        self.width = config.width or get_terminal_width()
        self.force_color = config.force_color
        self.output = output or self._get_utf8_output(sys.stdout)

        self.parser = MarkdownParser()
        self.formatter = MarkdownFormatter(
            self.theme_config,
            inline_code_color=config.inline_code_color,
            code_background=self.code_background,
            width=self.width,
            force_color=self.force_color,
        )

        self.buffer = ''
        self.state = RenderState()
        self._last_element = None
        self._last_output_ended_with_newline = False
        self._dim_mode = False

    def render(self, chunk, dim_mode=False):
        """
        Render a chunk of markdown content

        Args:
            chunk: Markdown text chunk from streaming response
            dim_mode: Enable dim/reduced color mode for this chunk
        """
        if chunk is None:
            return

        self._dim_mode = dim_mode

        chunk = strip_ansi(chunk)
        if isinstance(chunk, str):
            chunk = chunk.replace('\r\n', '\n').replace('\r', '\n')
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

        parts = self.buffer.split('\n')
        complete_lines = parts[:-1]
        tail = parts[-1]

        closing_idx = -1
        for idx, line in enumerate(complete_lines):
            fence = self.parser.parse_code_fence(line.strip())
            if fence is None:
                continue
            fence_length, language = fence
            if not language and fence_length >= self.state.code_fence_length:
                closing_idx = idx
                break

        if closing_idx >= 0:
            self._consume_code_lines(complete_lines[:closing_idx])
            if not self.stream_code:
                all_code = '\n'.join(self.state.code_lines)
                formatted = self.formatter.format_code_block(
                    all_code,
                    self.state.code_language,
                    self.line_numbers
                )
                self._write(formatted, 'code_block')
            self.state.reset_code()
            self.buffer = self._rebuild_buffer(
                complete_lines[closing_idx + 1:], tail
            )
            self._process_remaining_buffer()
        else:
            self._consume_code_lines(complete_lines)
            self.buffer = tail

    def _consume_code_lines(self, lines):
        if self.stream_code:
            for line in lines:
                self.state.code_line_count += 1
                self.state.code_lines.append(line)
                self._write_code_line(line)
        else:
            self.state.code_lines.extend(lines)

    @staticmethod
    def _rebuild_buffer(lines, tail):
        """Reassemble unprocessed buffered lines without losing newlines."""
        if tail:
            return '\n'.join(lines + [tail])
        if lines:
            return '\n'.join(lines) + '\n'
        return ''

    def _process_remaining_buffer(self):
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

    def _handle_table_buffer(self):
        """Process buffer when inside a table"""
        if '\n' not in self.buffer:
            return

        parts = self.buffer.split('\n')
        complete_lines = parts[:-1]
        tail = parts[-1]

        for i, line in enumerate(complete_lines):
            stripped = line.rstrip()
            table_row = self.parser.parse_table_row(stripped)
            if table_row is not None:
                if self.parser.is_separator_row(table_row):
                    self.state.table_alignments = self.parser.parse_table_alignments(table_row)
                else:
                    formatted_row = [self.parser.apply_inline_formatting(cell, self.formatter) for cell in table_row]
                    self.state.table_rows.append(formatted_row)
            else:
                if self.state.table_rows:
                    formatted = self.formatter.format_table(
                        self.state.table_rows, self.state.table_alignments
                    )
                    self._write(formatted, 'table')
                self.state.reset_table()
                self.buffer = self._rebuild_buffer(complete_lines[i:], tail)
                return

        self.buffer = tail

    def _flush_blockquote(self):
        """Render the buffered blockquote or alert."""
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

    def _process_line(self, line):
        """Process a single line of markdown"""
        stripped = line.rstrip()

        fence = self.parser.parse_code_fence(stripped)
        if fence is not None:
            fence_length, lang = fence
            if not self.state.in_code_block:
                self.state.in_code_block = True
                self.state.code_language = lang
                self.state.code_fence_length = fence_length
                self.state.code_lines = []
                self.state.code_line_count = 0
                return
            if not lang and fence_length >= self.state.code_fence_length:
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
            # A shorter fence or a fence with an info string is code content.
            # Fall through to the in-code-block branch below.

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
                self.state.table_alignments = []
            if self.parser.is_separator_row(table_row):
                self.state.table_alignments = self.parser.parse_table_alignments(table_row)
            else:
                formatted_row = [self.parser.apply_inline_formatting(cell, self.formatter) for cell in table_row]
                self.state.table_rows.append(formatted_row)
            return
        elif self.state.in_table:
            formatted = self.formatter.format_table(
                self.state.table_rows, self.state.table_alignments
            )
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
            formatted_text = self.parser.apply_inline_formatting(blockquote_text, self.formatter)
            self.state.blockquote_lines.append(formatted_text)
            return
        elif self.state.in_blockquote:
            self._flush_blockquote()
            # The current line ends the quote, so process it as a new element.
            self._process_line(line)
            return

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
            formatted = self.formatter.format_table(
                self.state.table_rows, self.state.table_alignments
            )
            self._write(formatted, 'table')
            self.state.reset_table()

        if self.state.in_blockquote:
            self._flush_blockquote()

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
        if self._last_element is not None and self._last_element != 'inline' and not self._last_output_ended_with_newline:
            self.output.write('\n')
        self._last_element = element_type

    def _write(self, text, element_type='inline'):
        """Write text to output with spacing management"""
        self._ensure_spacing(element_type)
        ended_with_newline = text.endswith('\n')
        if self._dim_mode:
            text = dim_text(text, force_color=self.force_color)
        try:
            self.output.write(text)
        except UnicodeEncodeError:
            # Fall back to ASCII so terminals with narrow encodings do not
            # crash on box-drawing characters or emoji.
            self.output.write(
                text.encode('ascii', errors='replace').decode('ascii')
            )
        self.output.flush()
        self._last_output_ended_with_newline = ended_with_newline

    def _write_code_line(self, line):
        highlighted = self.formatter.format_code_line(line, self.state.code_language)
        if self.line_numbers:
            num = self.state.code_line_count
            w = len(str(num))
            if w > self.state.code_line_num_width:
                self.state.code_line_num_width = w
            formatted = colorize(f'{num:>{self.state.code_line_num_width}}', Colors.BRIGHT_BLACK, force_color=self.force_color)
            output = f' {formatted}  {highlighted}'
        else:
            output = f'  {highlighted}'
        if self.code_background:
            output = self.formatter._apply_code_background(output)
        self._write(output + '\n', 'code_block')
