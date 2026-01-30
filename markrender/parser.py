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
    BOLD_PATTERN = re.compile(r'\*\*([^\*]+)\*\*')
    ITALIC_PATTERN = re.compile(r'\*([^\*]+)\*')
    STRIKETHROUGH_PATTERN = re.compile(r'~~([^~]+)~~')
    LINK_PATTERN = re.compile(r'\[([^\]]+)\]\(([^\)]+)\)')
    EMOJI_PATTERN = re.compile(r':([a-z0-9_+-]+):')
    CHECKBOX_PATTERN = re.compile(r'^(\s*)-\s+\[([ xX])\]\s+(.+)$', re.MULTILINE)
    LIST_ITEM_PATTERN = re.compile(r'^(\s*)[-*]\s+(.+)$', re.MULTILINE)
    ORDERED_LIST_PATTERN = re.compile(r'^(\s*)(\d+)\.\s+(.+)$', re.MULTILINE)
    BLOCKQUOTE_PATTERN = re.compile(r'^(>\s*)+(.+)$', re.MULTILINE)
    HR_PATTERN = re.compile(r'^(\*\*\*+|---+|___+)\s*$', re.MULTILINE)
    TABLE_ROW_PATTERN = re.compile(r'^\|(.+)\|$', re.MULTILINE)
    
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
        if '|' in text and not text.rstrip().endswith('|'):
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
            cells = [cell.strip() for cell in match.group(1).split('|')]
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
            Blockquote text or None
        """
        match = self.BLOCKQUOTE_PATTERN.match(line)
        if match:
            return match.group(2)
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
        Check if text contains incomplete inline markdown syntax
        
        Args:
            text: Text to check
            
        Returns:
            True if incomplete, False otherwise
        """
        if text.count('`') % 2 != 0:
            return True
        if text.count('**') % 2 != 0:
            return True
        if text.count('*') % 2 != 0:
            if re.search(r'^\s*\* ', text) is None:
                return True
        if text.count('~~') % 2 != 0:
            return True
        if text.count('[') > text.count(']'):
            return True
        if text.count('(') > text.count(')'):
            return True
        return False
    
    def apply_inline_formatting(self, text, formatter):
        """
        Apply inline formatting (code, bold, italic, links, emoji)
        
        Args:
            text: Text to format
            formatter: MarkdownFormatter instance
        
        Returns:
            Formatted text
        """
        # Replace inline code first (to avoid conflicts)
        def replace_inline_code(match):
            return formatter.format_inline_code(match.group(1))
        text = self.INLINE_CODE_PATTERN.sub(replace_inline_code, text)
        
        # Bold
        def replace_bold(match):
            return formatter.format_bold(match.group(1))
        text = self.BOLD_PATTERN.sub(replace_bold, text)
        
        # Italic
        def replace_italic(match):
            return formatter.format_italic(match.group(1))
        text = self.ITALIC_PATTERN.sub(replace_italic, text)
        
        # Strikethrough
        def replace_strikethrough(match):
            return formatter.format_strikethrough(match.group(1))
        text = self.STRIKETHROUGH_PATTERN.sub(replace_strikethrough, text)
        
        # Links
        def replace_link(match):
            return formatter.format_link(match.group(1), match.group(2))
        text = self.LINK_PATTERN.sub(replace_link, text)
        
        # Emoji
        def replace_emoji(match):
            return formatter.format_emoji(match.group(1))
        text = self.EMOJI_PATTERN.sub(replace_emoji, text)
        
        return text
