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
    LINK_PATTERN = re.compile(r'\[([^\]]+)\]\(([^\)]+)\)')
    EMOJI_PATTERN = re.compile(r':([a-z0-9_+-]+):')
    CHECKBOX_PATTERN = re.compile(r'^(\s*)-\s+\[([ xX])\]\s+(.+)$', re.MULTILINE)
    LIST_ITEM_PATTERN = re.compile(r'^(\s*)[-*]\s+(.+)$', re.MULTILINE)
    ORDERED_LIST_PATTERN = re.compile(r'^(\s*)(\d+)\.\s+(.+)$', re.MULTILINE)
    BLOCKQUOTE_PATTERN = re.compile(r'^((?:>\s?)+)(.*)$', re.MULTILINE)
    CALLOUT_PATTERN = re.compile(r'^\[!(NOTE|TIP|IMPORTANT|WARNING|CAUTION|ATTENTION)\]\s*(.*)$', re.IGNORECASE)
    HR_PATTERN = re.compile(r'^(\*\*\*+|---+|___+)\s*$', re.MULTILINE)
    TABLE_ROW_PATTERN = re.compile(r'^\s*\|.*\|\s*$', re.MULTILINE)
    
    def __init__(self):
        """Initialize parser state"""
        self.in_code_block = False
        self.code_language = ''
        self.code_buffer = []
        self.in_table = False
        self.table_buffer = []
    
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
        # Check for unclosed links (simplified)
        if text.count('[') > text.count(']'):
            return True
        if text.count('(') > text.count(')'):
             # Only if we have a preceding ']' might this be a link url
             if ']' in text:
                return True
        return False
    
    def apply_inline_formatting(self, text, formatter):
        """
        Apply inline formatting (code, bold, italic, links, emoji)
        Returns a rich.Text object.
        """
        from rich.text import Text
        
        if not text:
            return Text("")

        # 1. Handle Code Blocks (Highest Priority, disables other formatting)
        segments = split_by_regex(text, self.INLINE_CODE_PATTERN)
        
        final_text = Text()
        
        for segment in segments:
            content = segment['text']
            if segment['match']:
                # This is a code block
                code_content = segment['match'].group(1) 
                final_text.append(formatter.format_inline_code(code_content))
            else:
                # This is a plain text segment, process other formatting
                final_text.append(self._process_links_and_styles(content, formatter))
                
        return final_text
    
    def _process_links_and_styles(self, text, formatter):
        """
        Process links, bold, italic, strikethrough, emoji in that order.
        """
        from rich.text import Text
        
        # 2. Handle Links
        segments = split_by_regex(text, self.LINK_PATTERN)
        result = Text()
        
        for segment in segments:
            content = segment['text']
            if segment['match']:
                # It's a link: [text](url)
                link_text = segment['match'].group(1)
                link_url = segment['match'].group(2)
                
                # Recursively process the link text
                styled_link_text = self._process_styles_only(link_text, formatter)
                
                # Apply link style
                formatted_link = formatter.format_link(link_text, link_url)
                link_style = formatted_link.style
                
                styled_link_text.stylize(link_style)
                result.append(styled_link_text)
            else:
                # Not a link
                result.append(self._process_styles_only(content, formatter))
        return result

    def _process_styles_only(self, text, formatter):
        """
        Process bold, italic, strike, emoji.
        """
        # Bold
        segments = split_by_regex(text, self.BOLD_PATTERN)
        result_bold = self._process_segments(segments, formatter.format_bold, self._process_italic, formatter)
        return result_bold

    def _process_italic(self, text, formatter):
        segments = split_by_regex(text, self.ITALIC_PATTERN)
        return self._process_segments(segments, formatter.format_italic, self._process_strike, formatter)

    def _process_strike(self, text, formatter):
        segments = split_by_regex(text, self.STRIKETHROUGH_PATTERN)
        return self._process_segments(segments, formatter.format_strikethrough, self._process_emoji, formatter)

    def _process_emoji(self, text, formatter):
        segments = split_by_regex(text, self.EMOJI_PATTERN)
        from rich.text import Text
        result = Text()
        for segment in segments:
            if segment['match']:
                emoji_code = segment['match'].group(1)
                result.append(formatter.format_emoji(emoji_code))
            else:
                result.append(self._process_plain(segment['text'], formatter))
        return result

    def _process_plain(self, text, formatter):
        from rich.text import Text
        return Text(text)

    def _process_segments(self, segments, format_func, next_stage_func, formatter):
        from rich.text import Text
        result = Text()
        for segment in segments:
            content = segment['text']
            if segment['match']:
                inner = segment['match'].group(1)
                inner_processed = next_stage_func(inner, formatter)
                
                # Get style from format func
                example = format_func("dummy")
                style_to_apply = example.style
                
                inner_processed.stylize(style_to_apply)
                result.append(inner_processed)
            else:
                result.append(next_stage_func(content, formatter))
        return result

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