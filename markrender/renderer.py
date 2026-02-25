"""
Main markdown renderer for streaming LLM responses
"""

import sys
import re
import io
from .parser import MarkdownParser
from .formatters import MarkdownFormatter
from .themes import get_theme
from .colors import get_terminal_width
from .config import RendererConfig


# Ensure UTF-8 encoding on Windows
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except (AttributeError, io.UnsupportedOperation):
        # Fallback for older Python versions or when stdout is redirected
        pass


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
        stream_code=True,
        use_config=True,
        config=None,
        dim_mode=False
    ):
        """
        Initialize markdown renderer

        Args:
            theme: Syntax highlighting theme name (default: 'github-dark')
            code_background: Show background in code blocks (default: False)
            inline_code_color: Custom ANSI color for inline code (default: theme default)
            line_numbers: Show line numbers in code blocks (default: True)
            width: Terminal width (default: auto-detect)
            output: Output file object (default: sys.stdout)
            force_color: Force color output even if terminal does not support it (default: False)
            stream_code: Stream code blocks line by line (default: True).
            use_config: Load configuration from file (default: True)
            config: Optional RendererConfig instance
            dim_mode: Enable dim mode (dimmed text, reduced colors)
        """
        # Initialize configuration
        if config is not None:
            self.config = config
        elif use_config:
            self.config = RendererConfig.from_file()
        else:
            self.config = RendererConfig(
                theme=theme,
                code_background=code_background,
                inline_code_color=inline_code_color,
                line_numbers=line_numbers,
                width=width,
                force_color=force_color,
                stream_code=stream_code,
                dim_mode=dim_mode
            )
        
        # Override config with explicitly passed arguments if they are not defaults
        if theme != 'github-dark':
            self.config.config['theme'] = theme
        if code_background is not False:
            self.config.config['code_background'] = code_background
        if inline_code_color is not None:
            self.config.config['inline_code_color'] = inline_code_color
        if line_numbers is not True:
            self.config.config['line_numbers'] = line_numbers
        if width is not None:
            self.config.config['width'] = width
        if force_color is not False:
            self.config.config['force_color'] = force_color
        if stream_code is not True:
            self.config.config['stream_code'] = stream_code
        if dim_mode is not False:
            self.config.config['dim_mode'] = dim_mode
        
        self.theme_config = get_theme(self.config.theme)
        self.code_background = self.config.code_background
        self.line_numbers = self.config.line_numbers
        self.width = self.config.width or get_terminal_width()
        self.output = output or sys.stdout
        self.force_color = self.config.force_color
        self.stream_code = self.config.stream_code
        self.dim_mode = self.config.dim_mode
        
        # Initialize parser and formatter
        self.parser = MarkdownParser()
        self.formatter = MarkdownFormatter(
            self.theme_config,
            inline_code_color=self.config.inline_code_color,
            code_background=self.code_background,
            width=self.width,
            force_color=self.force_color,
            output=self.output,
            dim_mode=self.dim_mode
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
        self.in_list = False
        self.list_stack = []  # Stack to track nested lists [(indent_level, list_type, counter)]
        self.list_buffer = []  # Buffer for list items waiting to be rendered
        self.footnotes = {}  # Footnote definitions
        self.footnote_order = []  # Order of footnote references
    
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

    def _flush_list_buffer(self):
        """Flush buffered list items with proper nesting support"""
        if not self.list_buffer:
            self.in_list = False
            return

        # Sort and render list items with proper nesting
        # stack stores the indentation levels we've encountered
        stack = [] # list of indentation levels
        
        for item in self.list_buffer:
            indent = item['indent']
            text = item['text']
            is_ordered = item['ordered']
            
            # Find the level for this indentation
            if not stack or indent > stack[-1]:
                stack.append(indent)
            else:
                # Pop levels that are deeper than current indent
                while len(stack) > 1 and stack[-1] > indent:
                    stack.pop()
                # If we're at a new indent that's not in the stack but less than top,
                # we should technically handle it, but for now we'll just use the stack depth
                if indent < stack[-1]:
                     stack[-1] = indent
            
            current_level = len(stack) - 1
            
            # Track counter for ordered lists at each level
            # We'll use a simple approach: if it's the same level and same type as previous, increment
            # This is handled by the formatter usually but we need to provide the correct number
            
            # For simplicity, we'll let the formatter handle the bullet cycling based on level
            formatted_text = self.parser.apply_inline_formatting(text, self.formatter)
            formatted = self.formatter.format_list_item(
                formatted_text, 
                ordered=is_ordered, 
                number=item.get('number', 1), 
                indent_level=current_level
            )
            self._write(formatted + '\n')

        self.list_buffer = []
        self.in_list = False

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

        # Check if it's a list item first to avoid premature flushing
        ordered_item = self.parser.parse_ordered_list_item(stripped)
        unordered_item = self.parser.parse_list_item(stripped)
        is_list_item = ordered_item is not None or unordered_item is not None

        # If the line is a block-level element, flush the paragraph buffer.
        is_block = (
            self.parser.is_hr(stripped) or
            self.parser.parse_heading(stripped) or
            self.parser.parse_code_block_delimiter(stripped) is not None or
            self.parser.parse_table_row(stripped) is not None or 
            self.parser.BLOCKQUOTE_PATTERN.match(line) or
            self.parser.parse_checkbox(stripped) or
            is_list_item
        )

        if is_block and not self.in_table:
            self._flush_paragraph_buffer()
            
        # If it's NOT a list item but we are in a list, flush the list buffer
        if self.in_list and not is_list_item and not self.in_blockquote:
             # Check for continuation before flushing
             if stripped and line.startswith(' ' * 2) and not is_block:
                  if self.list_buffer:
                       self.list_buffer[-1]['text'] += ' ' + stripped
                       return
             
             # Not a continuation, flush the list
             if stripped or not self.finalizing: # Don't flush on empty line unless finalizing
                  self._flush_list_buffer()

        # Code block handling
        if self.in_code_block:
            if self.parser.parse_code_block_delimiter(stripped) is not None:
                if self.code_language == 'mermaid':
                    # Render mermaid diagram
                    code = '\n'.join(self.code_buffer)
                    formatted = self.formatter.format_mermaid_diagram(code)
                    self._write(formatted)
                elif self.code_language in ('tree', 'file-tree'):
                    # Render file tree
                    code = '\n'.join(self.code_buffer)
                    formatted = self.formatter.format_file_tree(code)
                    self._write(formatted)
                elif not self.stream_code:
                    code = '\n'.join(self.code_buffer)
                    formatted = self.formatter.format_code_block(code, self.code_language, self.line_numbers)
                    self._write(formatted)
                else:
                    self._write(self.formatter.end_code_block(self.code_language))
                self.in_code_block = False
                self.code_language = ''
                self.code_buffer = []
            else:
                if self.code_language in ('mermaid', 'tree', 'file-tree'):
                    self.code_buffer.append(line)
                elif self.stream_code:
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
                if lang in ('mermaid', 'tree', 'file-tree'):
                    # These blocks are rendered as a whole at the end
                    self.code_buffer = []
                elif self.stream_code:
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
        box_blockquote_data = self.parser.parse_box_blockquote(line)
        
        if blockquote_data or box_blockquote_data:
            if blockquote_data:
                blockquote_text, nesting_level = blockquote_data
            else:
                blockquote_text, nesting_level = box_blockquote_data

            if self.in_table:
                self._flush_table()

            if not self.in_blockquote:
                self.in_blockquote = True
                self.blockquote_lines = []

            self.blockquote_lines.append((blockquote_text.strip(), nesting_level))
            return
        elif self.in_blockquote:
            # Check if this line continues the blockquote
            # Continuation conditions:
            # 1. Line starts with whitespace (indented continuation)
            # 2. Line starts with │ or | (another box blockquote line)
            # 3. Line is a sentence continuation (starts with lowercase, indicating wrapped text)
            # BUT NOT if it's a horizontal rule or other block element
            is_sentence_continuation = stripped and stripped[0].islower()
            is_block_element = self.parser.is_hr(stripped)
            
            # Empty line ends the blockquote
            if not stripped:
                # Apply inline formatting to blockquote lines before rendering
                formatted_lines = []
                for line_content, line_level in self.blockquote_lines:
                    formatted_text = self.parser.apply_inline_formatting(line_content, self.formatter)
                    formatted_lines.append((formatted_text, line_level))
                formatted = self.formatter.format_blockquote(formatted_lines)
                self._write(formatted + '\n')
                self.in_blockquote = False
                self.blockquote_lines = []
                if is_block_element:
                    # Process the block element
                    self._process_line(line)
                return
            
            if (line.startswith(' ') or 
                line.startswith('\t') or
                self.parser.parse_box_blockquote(line) or
                (is_sentence_continuation and not is_block_element)):
                # This is a continuation of the blockquote
                if self.parser.parse_box_blockquote(line):
                    bb_data = self.parser.parse_box_blockquote(line)
                    self.blockquote_lines.append((bb_data[0].strip(), bb_data[1]))
                else:
                    self.blockquote_lines.append((stripped, 1))
                return
            else:
                # The blockquote has ended, so we need to format and print it.
                # Apply inline formatting to blockquote lines before rendering
                formatted_lines = []
                for line_content, line_level in self.blockquote_lines:
                    formatted_text = self.parser.apply_inline_formatting(line_content, self.formatter)
                    formatted_lines.append((formatted_text, line_level))
                formatted = self.formatter.format_blockquote(formatted_lines)
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

        # Footnote definition
        footnote_def = self.parser.parse_footnote_def(stripped)
        if footnote_def:
            footnote_id, content = footnote_def
            self.footnotes[footnote_id] = content
            if footnote_id not in self.footnote_order:
                self.footnote_order.append(footnote_id)
            return

        # Definition list (Term : Definition)
        definition = self.parser.parse_definition_item(stripped)
        if definition:
            if self.in_table:
                self._flush_table()
            term, def_text = definition
            term_formatted = self.parser.apply_inline_formatting(term, self.formatter)
            def_formatted = self.parser.apply_inline_formatting(def_text, self.formatter)
            formatted = self.formatter.format_definition_item(term_formatted, def_formatted)
            self._write(formatted + '\n')
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

        # Progress checkbox (e.g., - [50%] Task)
        progress_checkbox = self.parser.parse_progress_checkbox(stripped)
        if progress_checkbox:
            if self.in_table:
                self._flush_table()
            indent, percentage, text = progress_checkbox
            text = self.parser.apply_inline_formatting(text, self.formatter)
            formatted = self.formatter.format_progress_bar(percentage, text, indent)
            self._write(formatted + '\n')
            return

        # Ordered list
        if ordered_item:
            if self.in_table:
                self._flush_table()
            indent, number, text = ordered_item
            # Buffer the list item for nested processing
            if not self.in_list:
                self.in_list = True
            self.list_buffer.append({'indent': indent, 'text': text, 'ordered': True, 'number': number})
            return

        # Unordered list
        if unordered_item:
            if self.in_table:
                self._flush_table()
            indent, text, marker = unordered_item
            # Buffer the list item for nested processing
            if not self.in_list:
                self.in_list = True
            self.list_buffer.append({'indent': indent, 'text': text, 'ordered': False, 'marker': marker})
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
            # Apply inline formatting to blockquote lines before rendering
            formatted_lines = []
            for line_content, line_level in self.blockquote_lines:
                formatted_text = self.parser.apply_inline_formatting(line_content, self.formatter)
                formatted_lines.append((formatted_text, line_level))
            formatted = self.formatter.format_blockquote(formatted_lines)
            self._write(formatted + '\n')
            self.in_blockquote = False
            self.blockquote_lines = []

        # Flush any remaining list items
        if self.in_list and self.list_buffer:
            self._flush_list_buffer()

        # Render footnotes section
        if self.footnotes:
            footnotes_list = []
            for i, footnote_id in enumerate(self.footnote_order, 1):
                content = self.footnotes.get(footnote_id, '')
                content_formatted = self.parser.apply_inline_formatting(content, self.formatter)
                footnotes_list.append((footnote_id, content_formatted, i))
            
            footnotes_section = self.formatter.format_footnotes_section(footnotes_list)
            self._write(footnotes_section)

        # Flush output
        self.output.flush()
        self.finalizing = False
    
    def _write(self, text):
        """Write text to output with robust Unicode handling"""
        # Always use rich console to print, so markup is rendered
        if self.formatter.console:
            try:
                # Print directly to the console which handles the output
                # Handle potential Unicode errors gracefully
                if isinstance(text, str):
                    # Ensure UTF-8 safe encoding
                    text = text.encode('utf-8', errors='replace').decode('utf-8')
                
                # Use overflow='fold' to prevent word cutting and ensure robust wrapping
                self.formatter.console.print(text, end='', overflow='fold')
            except Exception as e:
                # Fallback: try to print without formatting
                try:
                    self.output.write(str(text))
                except Exception:
                    # Last resort: skip problematic content
                    pass
        else:
            # Fallback if rich is not available
            try:
                if isinstance(text, str):
                    text = text.encode('utf-8', errors='replace').decode('utf-8')
                self.output.write(str(text))
            except Exception:
                # Skip problematic content
                pass
        self.output.flush()
