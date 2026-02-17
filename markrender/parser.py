"""
Markdown parser for incremental/streaming parsing
Handles chunk-by-chunk markdown element detection
"""

import re


class MarkdownParser:
    """Incremental markdown parser for streaming content"""
    
    # Regex patterns for markdown elements
    HEADING_PATTERN = re.compile(r'^(#{1,6})\s+(.+)$', re.MULTILINE)
    CODE_BLOCK_START = re.compile(r'^\s*```(\w*)\s*$', re.MULTILINE)
    INLINE_CODE_PATTERN = re.compile(r'`([^`]+)`')
    BOLD_PATTERN = re.compile(r'\*\*(.+?)\*\*')
    ITALIC_PATTERN = re.compile(r'\*([^\*]+)\*')
    STRIKETHROUGH_PATTERN = re.compile(r'~~([^~]+)~~')
    HIGHLIGHT_PATTERN = re.compile(r'==([^=]+)==')
    LINK_PATTERN = re.compile(r'\[([^\]]+)\]\(([^\)]+)\)')
    # Also support angle bracket links: <url>
    ANGLE_LINK_PATTERN = re.compile(r'<([a-zA-Z][a-zA-Z0-9+.-]*://[^>]+)>')
    # Image pattern: ![alt text](url)
    IMAGE_PATTERN = re.compile(r'!\[([^\]]*)\]\(([^\)]+)\)')
    # Footnote reference: [^1] or [^name]
    FOOTNOTE_REF_PATTERN = re.compile(r'\[\^([^\]]+)\]')
    # Footnote definition: [^1]: content
    FOOTNOTE_DEF_PATTERN = re.compile(r'^\[\^([^\]]+)\]:\s*(.+)$', re.MULTILINE)
    EMOJI_PATTERN = re.compile(r':([a-z0-9_+-]+):')
    CHECKBOX_PATTERN = re.compile(r'^(\s*)-\s+\[([ xX])\]\s+(.+)$', re.MULTILINE)
    PROGRESS_CHECKBOX_PATTERN = re.compile(r'^(\s*)-\s+\[(\d{1,3})%\]\s*(.*)$', re.MULTILINE)
    LIST_ITEM_PATTERN = re.compile(r'^(\s*)[-*•]\s+(.+)$', re.MULTILINE)
    ORDERED_LIST_PATTERN = re.compile(r'^(\s*)(\d+)\.\s+(.+)$', re.MULTILINE)
    # Definition list: Term : Definition (requires space before and after colon, no emoji patterns)
    DEFINITION_LIST_PATTERN = re.compile(r'^([A-Za-z][^\s:].*?)\s{2,}:\s{2,}(.+)$')
    BLOCKQUOTE_PATTERN = re.compile(r'^((?:>\s?)+)(.*)$', re.MULTILINE)
    # Also support box-drawing character │ for blockquotes (common in some markdown styles)
    BOX_BLOCKQUOTE_PATTERN = re.compile(r'^(\s*[│|](?:\s*[│|])*)\s*(.*)$')
    CALLOUT_PATTERN = re.compile(r'^\[!(NOTE|TIP|IMPORTANT|WARNING|CAUTION|ATTENTION|INFO|SUCCESS|QUESTION|FAILURE|BUG|EXAMPLE|QUOTE)\]\s*(.*)$', re.IGNORECASE)
    HR_PATTERN = re.compile(r'^(\*\*\*+|---+|___+)\s*$', re.MULTILINE)
    TABLE_ROW_PATTERN = re.compile(r'^\s*\|.*\|\s*$', re.MULTILINE)
    # LaTeX math patterns (to preserve as raw text)
    # DOTALL flag allows . to match newlines for multi-line display math
    LATEX_INLINE_PATTERN = re.compile(r'\\\((.+?)\\\)', re.DOTALL)
    LATEX_DISPLAY_PATTERN = re.compile(r'\\\[(.+?)\\\]', re.DOTALL)
    
    def __init__(self):
        """Initialize parser state"""
        self.in_code_block = False
        self.code_language = ''
        self.code_buffer = []
        self.in_table = False
        self.table_buffer = []
        self.in_latex_inline = False
        self.in_latex_display = False
        self.footnotes = {}  # Dictionary to store footnote definitions
        self.footnote_order = []  # List to maintain footnote order
    
    def is_complete_element(self, text):
        """
        Check if text contains a complete markdown element
        or if we need more content

        Args:
            text: Text to check

        Returns:
            Tuple of (is_complete, element_type)
        """
        # Check for incomplete code block
        if '```' in text:
            backtick_count = text.count('```')
            if backtick_count % 2 == 1:
                return (False, 'code_block')

        # Check for incomplete table
        if '|' in text:
            # Check if it looks like a table row but isn't complete
            # This is a bit loose, but we want to catch " | col1 | col"
            stripped = text.strip()
            if stripped.startswith('|') and not stripped.endswith('|'):
                 return (False, 'table')

        # Check for incomplete inline code
        if text.count('`') % 2 == 1:
            return (False, 'inline_code')

        # Check for incomplete LaTeX expressions
        if text.count('\\(') != text.count('\\)'):
            return (False, 'latex_inline')
        if text.count('\\[') != text.count('\\]'):
            return (False, 'latex_display')

        return (True, None)
    
    def parse_heading(self, line):
        """
        Parse heading from line
        
        Args:
            line: Line to parse
        
        Returns:
            Tuple of (level, text) or None
        """
        match = self.HEADING_PATTERN.match(line)
        if match:
            level = len(match.group(1))
            text = match.group(2)
            return (level, text)
        return None
    
    def parse_code_block_delimiter(self, line):
        """
        Check if line is a code block delimiter
        
        Args:
            line: Line to check
        
        Returns:
            Language name if delimiter, None otherwise
        """
        match = self.CODE_BLOCK_START.match(line)
        if match:
            return match.group(1) or ''
        return None
    
    def parse_table_row(self, line):
        """
        Parse table row from line
        
        Args:
            line: Line to parse
        
        Returns:
            List of cells, empty list for separator rows, or None if not a table row
        """
        match = self.TABLE_ROW_PATTERN.match(line)
        if match:
            # For "| A | B |", line.split('|') gives ['', ' A ', ' B ', '']
            # We need to strip and remove the leading/trailing empty strings
            # Handle escaped pipes if necessary (simplified for now)
            stripped_line = line.strip()
            if not stripped_line.startswith('|') or not stripped_line.endswith('|'):
                return None
                
            raw_cells = stripped_line.split('|')
            # Remove the first and last empty strings from the split (due to leading/trailing '|')
            cells = [cell.strip() for cell in raw_cells[1:-1]]
            
            # Check if it's a separator row (----)
            if cells and all(re.match(r'^:?-+:?$', cell) for cell in cells):
                # Return empty list to indicate separator (keep table open)
                return []
            return cells
        return None
    
    def parse_checkbox(self, line):
        """
        Parse checkbox from line

        Args:
            line: Line to parse

        Returns:
            Tuple of (checked, text) or None
        """
        match = self.CHECKBOX_PATTERN.match(line)
        if match:
            checked = match.group(2).lower() == 'x'
            text = match.group(3)
            return (checked, text)
        return None

    def parse_image(self, text):
        """
        Parse image from text

        Args:
            text: Text to parse

        Returns:
            Tuple of (alt_text, url) or None
        """
        match = self.IMAGE_PATTERN.search(text)
        if match:
            alt_text = match.group(1)
            url = match.group(2)
            return (alt_text, url)
        return None

    def parse_footnote_def(self, line):
        """
        Parse footnote definition from line

        Args:
            line: Line to parse

        Returns:
            Tuple of (footnote_id, content) or None
        """
        match = self.FOOTNOTE_DEF_PATTERN.match(line)
        if match:
            footnote_id = match.group(1)
            content = match.group(2)
            return (footnote_id, content)
        return None

    def parse_footnote_ref(self, text):
        """
        Parse footnote reference from text

        Args:
            text: Text to parse

        Returns:
            List of footnote IDs found or empty list
        """
        return self.FOOTNOTE_REF_PATTERN.findall(text)

    def parse_definition_item(self, line):
        """
        Parse definition list item (Term : Definition)

        Args:
            line: Line to parse

        Returns:
            Tuple of (term, definition) or None
        """
        match = self.DEFINITION_LIST_PATTERN.match(line)
        if match:
            term = match.group(1).strip()
            definition = match.group(2).strip()
            return (term, definition)
        return None

    def parse_progress_checkbox(self, line):
        """
        Parse progress checkbox (e.g., - [50%] Task name)

        Args:
            line: Line to parse

        Returns:
            Tuple of (indent, percentage, text) or None
        """
        match = self.PROGRESS_CHECKBOX_PATTERN.match(line)
        if match:
            indent = len(match.group(1)) // 2
            percentage = min(100, max(0, int(match.group(2))))
            text = match.group(3)
            return (indent, percentage, text)
        return None

    def parse_list_item(self, line):
        """
        Parse unordered list item from line
        
        Args:
            line: Line to parse
        
        Returns:
            Tuple of (indent_level, text) or None
        """
        match = self.LIST_ITEM_PATTERN.match(line)
        if match:
            indent = len(match.group(1)) // 2
            text = match.group(2)
            return (indent, text)
        return None
    
    def parse_ordered_list_item(self, line):
        """
        Parse ordered list item from line
        
        Args:
            line: Line to parse
        
        Returns:
            Tuple of (indent_level, number, text) or None
        """
        match = self.ORDERED_LIST_PATTERN.match(line)
        if match:
            indent = len(match.group(1)) // 2
            number = int(match.group(2))
            text = match.group(3)
            return (indent, number, text)
        return None
    
    def parse_blockquote(self, line):
        """
        Parse blockquote from line

        Args:
            line: Line to parse

        Returns:
            Tuple of (text, nesting_level) or None
        """
        match = self.BLOCKQUOTE_PATTERN.match(line)
        if match:
            markers = match.group(1)
            text = match.group(2)
            # Count the number of '>' characters to determine nesting level
            nesting_level = markers.count('>')
            return (text, nesting_level)
        return None

    def parse_box_blockquote(self, line):
        """
        Parse blockquote using box-drawing character │ or pipe |

        Args:
            line: Line to parse

        Returns:
            Tuple of (text, level) or None
        """
        match = self.BOX_BLOCKQUOTE_PATTERN.match(line)
        if match:
            markers = match.group(1)
            text = match.group(2)
            # Count the number of │ or | characters to determine nesting level
            nesting_level = max(markers.count('│'), markers.count('|'))
            if text.strip() or nesting_level > 0:
                return (text, nesting_level)
        return None

    def is_hr(self, line):
        """
        Check if line is a horizontal rule
        
        Args:
            line: Line to check
        
        Returns:
            True if HR, False otherwise
        """
        return bool(self.HR_PATTERN.match(line))

    def is_inline_incomplete(self, text):
        """
        Check if text contains incomplete inline markdown syntax across chunks.
        This is a heuristic to prevent flushing paragraphs with unclosed inline elements.

        Args:
            text: Text to check

        Returns:
            True if incomplete, False otherwise
        """
        # Check for unclosed inline code blocks
        if text.count('`') % 2 != 0:
            return True
        # Check for unclosed bold or italic (common markers are **, *, __, _)
        # This is a simplified check for streaming; a full markdown parser would handle this more robustly.
        if text.count('**') % 2 != 0:
            return True
        if text.count('*') % 2 != 0:
            # Only consider it incomplete if it's not part of a list item
            if re.search(r'^\s*\* ', text) is None:
                return True
        if text.count('__') % 2 != 0:
            return True
        if text.count('_') % 2 != 0:
             # Underscores are tricky within words, but for streaming cut-off, odd count is a good heuristic
            return True
        # Check for unclosed strikethrough
        if text.count('~~') % 2 != 0:
            return True
        # Check for unclosed highlight
        if text.count('==') % 2 != 0:
            return True
        # Check for unclosed links (simplified)
        if text.count('[') > text.count(']'):
            return True
        if text.count('(') > text.count(')'):
             # Only if we have a preceding ']' might this be a link url
             if ']' in text:
                return True
        # Check for incomplete LaTeX expressions
        if text.count('\\(') != text.count('\\)'):
            return True
        if text.count('\\[') != text.count('\\]'):
            return True
        # Check for incomplete angle bracket links
        if text.count('<') > text.count('>'):
            # Could be an incomplete angle link
            if re.search(r'<[a-zA-Z]', text) and not re.search(r'>', text[text.rfind('<'):]):
                return True
        return False
    
    def apply_inline_formatting(self, text, formatter):
        """
        Apply inline formatting (code, bold, italic, links, strikethrough, emoji) in the correct order.
        Returns a rich.Text object.
        """
        from rich.text import Text

        if not text:
            return Text("")

        # Replace HTML line breaks with actual newlines before processing
        text = text.replace('<br>', '\n').replace('<br/>', '\n').replace('<br />', '\n')

        # Process formatting in order of specificity to avoid conflicts:
        # 1. Inline code (most specific - avoid processing formatting inside code)
        # 2. LaTeX math (preserve as-is, add line breaks for display math)
        # 3. Links (including angle bracket links)
        # 4. Bold/Italic/Strikethrough
        # 5. Emoji

        # First, handle LaTeX expressions and angle links by replacing them with placeholders
        latex_parts = []
        angle_link_parts = []
        image_parts = []
        footnote_parts = []
        latex_placeholder = '\x00LATEXPLACEHOLDER{}\x00'
        angle_link_placeholder = '\x00ANGLELINKPLACEHOLDER{}\x00'
        image_placeholder = '\x00IMAGEPLACEHOLDER{}\x00'
        footnote_placeholder = '\x00FOOTNOTEPLACEHOLDER{}\x00'

        def save_latex(match):
            latex_parts.append(('inline', match.group(0)))
            return latex_placeholder.format(len(latex_parts) - 1)

        def save_display_latex(match):
            latex_parts.append(('display', match.group(0)))
            return latex_placeholder.format(len(latex_parts) - 1)

        def save_angle_link(match):
            angle_link_parts.append(match.group(1))  # Save just the URL
            return angle_link_placeholder.format(len(angle_link_parts) - 1)

        def save_image(match):
            image_parts.append((match.group(1), match.group(2)))  # (alt_text, url)
            return image_placeholder.format(len(image_parts) - 1)

        def save_footnote(match):
            footnote_id = match.group(1)
            footnote_parts.append(footnote_id)
            return footnote_placeholder.format(len(footnote_parts) - 1)

        # Save display math first (more specific)
        text = self.LATEX_DISPLAY_PATTERN.sub(save_display_latex, text)
        # Then save inline math
        text = self.LATEX_INLINE_PATTERN.sub(save_latex, text)
        # Save angle bracket links
        text = self.ANGLE_LINK_PATTERN.sub(save_angle_link, text)
        # Save images
        text = self.IMAGE_PATTERN.sub(save_image, text)
        # Save footnote references
        text = self.FOOTNOTE_REF_PATTERN.sub(save_footnote, text)

        # First, handle inline code separately to avoid processing formatting inside code
        code_parts = self._split_by_inline_code(text)

        result = Text()
        for i, part in enumerate(code_parts):
            if i % 2 == 1:  # This is a code part (odd indices are code, even are non-code)
                result.append(formatter.format_inline_code(part))
            else:  # This is a non-code part
                # Process other formatting in this non-code part
                formatted_part = self._apply_non_code_formatting(part, formatter)
                result.append(formatted_part)

        # Now restore LaTeX expressions and angle links while preserving styling
        # We need to rebuild the text with placeholders replaced
        result_text = result.plain
        
        # Find all placeholder positions and their lengths
        replacements = []  # List of (start, end, replacement_text)
        
        for i, (latex_type, latex) in enumerate(latex_parts):
            placeholder = latex_placeholder.format(i)
            start = result_text.find(placeholder)
            if start != -1:
                # Add line breaks around display math
                if latex_type == 'display':
                    replacement = '\n' + latex + '\n'
                else:
                    replacement = latex
                replacements.append((start, start + len(placeholder), replacement))
        
        for i, url in enumerate(angle_link_parts):
            placeholder = angle_link_placeholder.format(i)
            start = result_text.find(placeholder)
            if start != -1:
                replacements.append((start, start + len(placeholder), url))

        for i, (alt_text, url) in enumerate(image_parts):
            placeholder = image_placeholder.format(i)
            start = result_text.find(placeholder)
            if start != -1:
                # Replace with formatted image placeholder
                image_display = formatter.format_image(alt_text, url)
                replacements.append((start, start + len(placeholder), image_display))

        for i, footnote_id in enumerate(footnote_parts):
            placeholder = footnote_placeholder.format(i)
            start = result_text.find(placeholder)
            if start != -1:
                # Replace with formatted footnote reference (convert Text to string)
                footnote_num = i + 1
                footnote_display = formatter.format_footnote_ref(footnote_id, footnote_num)
                replacements.append((start, start + len(placeholder), footnote_display.plain))

        # Sort replacements by position (in reverse order to replace from end to start)
        replacements.sort(key=lambda x: x[0], reverse=True)
        
        # Apply replacements to the text
        for start, end, replacement in replacements:
            result_text = result_text[:start] + replacement + result_text[end:]
        
        # Create new Text object and re-apply styles from original spans
        final_result = Text(result_text)
        
        # Copy spans from original result, adjusting positions
        for span in result.spans:
            # Adjust span positions based on replacements
            new_start = span.start
            new_end = span.end
            
            # Calculate position adjustments
            for orig_start, orig_end, replacement in replacements:
                placeholder_len = orig_end - orig_start
                replacement_len = len(replacement)
                diff = replacement_len - placeholder_len
                
                if orig_start < new_start:
                    new_start += diff
                if orig_start < new_end:
                    new_end += diff
            
            # Only add span if it's valid
            if new_start < new_end and new_start >= 0 and new_end <= len(result_text):
                final_result.stylize(span.style, new_start, new_end)
        
        return final_result
    
    def _split_by_inline_code(self, text):
        """
        Split text by inline code markers, alternating between non-code and code parts.
        Returns a list where even indices are non-code parts and odd indices are code parts.
        """
        import re
        # Find all inline code sections
        parts = []
        last_end = 0
        
        for match in self.INLINE_CODE_PATTERN.finditer(text):
            start, end = match.span()
            
            # Add the non-code part before this match
            if start > last_end:
                parts.append(text[last_end:start])
            
            # Add the code content (without the backticks)
            code_content = match.group(1)
            parts.append(code_content)
            
            last_end = end
        
        # Add the remaining non-code part
        if last_end < len(text):
            parts.append(text[last_end:])
        
        return parts
    
    def _apply_non_code_formatting(self, text, formatter):
        """
        Apply non-code inline formatting (links, bold, italic, strikethrough, emoji) to text.
        """
        from rich.text import Text
        
        if not text:
            return Text("")
        
        # Process links first using the split_by_regex utility
        link_segments = split_by_regex(text, self.LINK_PATTERN)
        
        result = Text()
        for segment in link_segments:
            content = segment['text']
            if segment['match']:
                # It's a link: [text](url)
                link_text = segment['match'].group(1)
                link_url = segment['match'].group(2)

                # Apply other formatting to the link text
                formatted_link_text = self._apply_other_formatting(link_text, formatter)

                # Apply link style
                formatted_link = formatter.format_link(link_text, link_url)
                link_style = formatted_link.style

                formatted_link_text.stylize(link_style)
                result.append(formatted_link_text)
            else:
                # Not a link, process other formatting
                result.append(self._apply_other_formatting(content, formatter))
        return result
    
    def _apply_other_formatting(self, text, formatter):
        """
        Apply other formatting (bold, italic, strikethrough, emoji) to text.
        """
        from rich.text import Text
        
        if not text:
            return Text("")
        
        # Apply formatting in order of complexity
        # First, handle bold
        bold_parts = self._split_by_bold(text)
        
        result = Text()
        for i, part in enumerate(bold_parts):
            if i % 2 == 1:  # This is a bold part
                formatted_part = self._apply_non_bold_formatting(part, formatter)
                bold_style = formatter.format_bold("").style
                formatted_part.stylize(bold_style)
                result.append(formatted_part)
            else:  # This is a non-bold part
                result.append(self._apply_non_bold_formatting(part, formatter))
        
        return result
    
    def _split_by_bold(self, text):
        """
        Split text by bold markers, alternating between non-bold and bold parts.
        """
        import re
        parts = []
        last_end = 0
        
        for match in self.BOLD_PATTERN.finditer(text):
            start, end = match.span()
            
            # Add the non-bold part before this match
            if start > last_end:
                parts.append(text[last_end:start])
            
            # Add the bold content (without the **)
            bold_content = match.group(1)
            parts.append(bold_content)
            
            last_end = end
        
        # Add the remaining non-bold part
        if last_end < len(text):
            parts.append(text[last_end:])
        
        return parts
    
    def _apply_non_bold_formatting(self, text, formatter):
        """
        Apply non-bold formatting (italic, strikethrough, emoji) to text.
        """
        from rich.text import Text
        
        if not text:
            return Text("")
        
        # Handle italic
        italic_parts = self._split_by_italic(text)
        
        result = Text()
        for i, part in enumerate(italic_parts):
            if i % 2 == 1:  # This is an italic part
                formatted_part = self._apply_non_italic_formatting(part, formatter)
                italic_style = formatter.format_italic("").style
                formatted_part.stylize(italic_style)
                result.append(formatted_part)
            else:  # This is a non-italic part
                result.append(self._apply_non_italic_formatting(part, formatter))
        
        return result
    
    def _split_by_italic(self, text):
        """
        Split text by italic markers, alternating between non-italic and italic parts.
        """
        import re
        parts = []
        last_end = 0
        
        for match in self.ITALIC_PATTERN.finditer(text):
            start, end = match.span()
            
            # Add the non-italic part before this match
            if start > last_end:
                parts.append(text[last_end:start])
            
            # Add the italic content (without the *)
            italic_content = match.group(1)
            parts.append(italic_content)
            
            last_end = end
        
        # Add the remaining non-italic part
        if last_end < len(text):
            parts.append(text[last_end:])
        
        return parts
    
    def _apply_non_italic_formatting(self, text, formatter):
        """
        Apply non-italic formatting (strikethrough, emoji) to text.
        """
        from rich.text import Text
        
        if not text:
            return Text("")
        
        # Handle strikethrough
        strike_parts = self._split_by_strikethrough(text)
        
        result = Text()
        for i, part in enumerate(strike_parts):
            if i % 2 == 1:  # This is a strikethrough part
                formatted_part = self._apply_non_strike_formatting(part, formatter)
                strike_style = formatter.format_strikethrough("").style
                formatted_part.stylize(strike_style)
                result.append(formatted_part)
            else:  # This is a non-strikethrough part
                result.append(self._apply_non_strike_formatting(part, formatter))
        
        return result
    
    def _split_by_strikethrough(self, text):
        """
        Split text by strikethrough markers, alternating between non-strike and strike parts.
        """
        import re
        parts = []
        last_end = 0
        
        for match in self.STRIKETHROUGH_PATTERN.finditer(text):
            start, end = match.span()
            
            # Add the non-strikethrough part before this match
            if start > last_end:
                parts.append(text[last_end:start])
            
            # Add the strikethrough content (without the ~~)
            strike_content = match.group(1)
            parts.append(strike_content)
            
            last_end = end
        
        # Add the remaining non-strikethrough part
        if last_end < len(text):
            parts.append(text[last_end:])
        
        return parts
    
    def _apply_non_strike_formatting(self, text, formatter):
        """
        Apply non-strikethrough formatting (highlight, emoji) to text.
        """
        from rich.text import Text

        if not text:
            return Text("")

        # Handle highlight
        highlight_parts = self._split_by_highlight(text)

        result = Text()
        for i, part in enumerate(highlight_parts):
            if i % 2 == 1:  # This is a highlight part
                formatted_part = self._apply_non_highlight_formatting(part, formatter)
                highlight_style = formatter.format_highlight("").style
                formatted_part.stylize(highlight_style)
                result.append(formatted_part)
            else:  # This is a non-highlight part
                result.append(self._apply_non_highlight_formatting(part, formatter))

        return result

    def _split_by_highlight(self, text):
        """
        Split text by highlight markers, alternating between non-highlight and highlight parts.
        """
        import re
        parts = []
        last_end = 0

        for match in self.HIGHLIGHT_PATTERN.finditer(text):
            start, end = match.span()

            # Add the non-highlight part before this match
            if start > last_end:
                parts.append(text[last_end:start])

            # Add the highlight content (without the ==)
            highlight_content = match.group(1)
            parts.append(highlight_content)

            last_end = end

        # Add the remaining non-highlight part
        if last_end < len(text):
            parts.append(text[last_end:])

        return parts

    def _apply_non_highlight_formatting(self, text, formatter):
        """
        Apply non-highlight formatting (emoji) to text.
        """
        from rich.text import Text

        if not text:
            return Text("")

        # Handle emoji
        emoji_parts = self._split_by_emoji(text)

        result = Text()
        for i, part in enumerate(emoji_parts):
            if i % 2 == 1:  # This is an emoji part
                result.append(formatter.format_emoji(part))
            else:  # This is a non-emoji part
                result.append(Text(part))

        return result
    
    def _split_by_emoji(self, text):
        """
        Split text by emoji markers, alternating between non-emoji and emoji parts.
        """
        import re
        parts = []
        last_end = 0
        
        for match in self.EMOJI_PATTERN.finditer(text):
            start, end = match.span()
            
            # Add the non-emoji part before this match
            if start > last_end:
                parts.append(text[last_end:start])
            
            # Add the emoji code (without the colons)
            emoji_code = match.group(1)
            parts.append(emoji_code)
            
            last_end = end
        
        # Add the remaining non-emoji part
        if last_end < len(text):
            parts.append(text[last_end:])
        
        return parts
    

def split_by_regex(text, pattern):
    """
    Splits text by regex matches.
    Returns list of dicts: {'text': str, 'match': MatchObject|None}
    """
    segments = []
    last_end = 0
    for match in pattern.finditer(text):
        start, end = match.span()
        if start > last_end:
            segments.append({'text': text[last_end:start], 'match': None})
        
        segments.append({'text': text[start:end], 'match': match})
        last_end = end
    
    if last_end < len(text):
        segments.append({'text': text[last_end:], 'match': None})
        
    return segments