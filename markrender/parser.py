"""
Markdown parser for incremental/streaming parsing
Handles chunk-by-chunk markdown element detection
"""

import re

from .colors import strip_ansi


class MarkdownParser:
    """Incremental markdown parser for streaming content"""

    HEADING_PATTERN = re.compile(r"^(#{1,6})\s+(.+)$", re.MULTILINE)
    CODE_BLOCK_START = re.compile(r"^\s*(`{3,})([^`]*)$", re.MULTILINE)
    INLINE_CODE_PATTERN = re.compile(r"(?<!\\)(`{1,3})(.+?)(?<!\\)\1(?!`)")
    BOLD_ITALIC_PATTERN = re.compile(r"\*\*\*(?![\s*])(.+?)(?<![\s*])\*\*\*")
    BOLD_NESTED_PATTERN = re.compile(
        r"\*\*(?![\s*])((?:[^*]+|\*(?![\s*])[^*]+?\*)+?)\*\*"
    )
    ITALIC_NESTED_PATTERN = re.compile(
        r"(?<!\*)\*(?![\s*])((?:[^*]+|\*\*(?![\s*])[^*]+?\*\*)+?)\*(?!\*)"
    )
    BOLD_PATTERN = re.compile(r"\*\*(?![\s*])(.+?)(?<![\s*])\*\*")
    ITALIC_PATTERN = re.compile(r"(?<!\*)\*(?![\s*])([^*]+?)(?<![\s*])\*(?!\*)")
    STRIKETHROUGH_PATTERN = re.compile(r"~~([^~]+)~~")
    LINK_PATTERN = re.compile(r"\[([^\]]+)\]\(((?:[^\s()]|\([^\s()]*\))*)\)")
    IMAGE_PATTERN = re.compile(r"!\[([^\]]*)\]\(((?:[^\s()]|\([^\s()]*\))*)\)")
    EMOJI_PATTERN = re.compile(r":([a-z0-9_+-]+):")
    CHECKBOX_PATTERN = re.compile(r"^(\s*)[-*+]\s+\[([ xX])\]\s+(.+)$", re.MULTILINE)
    LIST_ITEM_PATTERN = re.compile(r"^(\s*)[-*+]\s+(.+)$", re.MULTILINE)
    ORDERED_LIST_PATTERN = re.compile(r"^(\s*)(\d+)\.\s+(.+)$", re.MULTILINE)
    BLOCKQUOTE_PATTERN = re.compile(r"^ {0,3}>\s+(.+)$", re.MULTILINE)
    ALERT_PATTERN = re.compile(
        r"^ {0,3}>\s*\[!(NOTE|TIP|IMPORTANT|WARNING|CAUTION)\]\s*$", re.MULTILINE
    )
    HR_PATTERN = re.compile(r"^(\*\*\*+|---+|___+)\s*$", re.MULTILINE)
    TABLE_ROW_PATTERN = re.compile(r"^\|(.+)\|$", re.MULTILINE)

    def __init__(self):
        self.in_code_block = False
        self.code_language = ""
        self.code_buffer = []
        self.in_table = False
        self.table_buffer = []

    def parse_heading(self, line):
        match = self.HEADING_PATTERN.match(line)
        if match:
            level = len(match.group(1))
            text = match.group(2)
            return (level, text)
        return None

    def parse_code_fence(self, line):
        """Return (fence_length, language) for a code fence, else None."""
        match = self.CODE_BLOCK_START.match(line)
        if match:
            info = match.group(2).strip()
            language = info.split()[0] if info else ""
            return len(match.group(1)), language
        return None

    def parse_code_block_delimiter(self, line):
        fence = self.parse_code_fence(line)
        if fence is not None:
            return fence[1]
        return None

    def parse_table_row(self, line):
        match = self.TABLE_ROW_PATTERN.match(line)
        if match:
            cells = [cell.strip() for cell in match.group(1).split("|")]
            return cells
        return None

    @staticmethod
    def is_separator_row(cells):
        return bool(cells and all(re.match(r"^:?-+:?$", cell) for cell in cells))

    @staticmethod
    def parse_table_alignments(cells):
        """Return the alignment for each column from a separator row."""
        alignments = []
        for cell in cells:
            cell = cell.strip()
            left = cell.startswith(':')
            right = cell.endswith(':')
            if left and right:
                alignments.append('center')
            elif right:
                alignments.append('right')
            else:
                alignments.append('left')
        return alignments

    def parse_checkbox(self, line):
        match = self.CHECKBOX_PATTERN.match(line)
        if match:
            checked = match.group(2).lower() == "x"
            text = match.group(3)
            return (checked, text)
        return None

    def parse_list_item(self, line):
        match = self.LIST_ITEM_PATTERN.match(line)
        if match:
            indent = len(match.group(1)) // 2
            text = match.group(2)
            return (indent, text)
        return None

    def parse_ordered_list_item(self, line):
        match = self.ORDERED_LIST_PATTERN.match(line)
        if match:
            indent = len(match.group(1)) // 2
            number = int(match.group(2))
            text = match.group(3)
            return (indent, number, text)
        return None

    def parse_blockquote(self, line):
        match = self.BLOCKQUOTE_PATTERN.match(line)
        if match:
            return match.group(1)
        return None

    @staticmethod
    def parse_alert(line):
        match = MarkdownParser.ALERT_PATTERN.match(line)
        if match:
            return match.group(1)
        return None

    def is_hr(self, line):
        return bool(self.HR_PATTERN.match(line))

    def apply_inline_formatting(self, text, formatter):
        text = strip_ansi(text)

        # Stash code spans so their contents are not formatted as markdown.
        code_spans = []

        def replace_inline_code(match):
            code_spans.append(formatter.format_inline_code(match.group(2)))
            return f"\x00{len(code_spans) - 1}\x00"

        text = self.INLINE_CODE_PATTERN.sub(replace_inline_code, text)

        # Images before links so the leading "!" is not left behind.
        def replace_image(match):
            alt = self.apply_inline_formatting(match.group(1), formatter)
            return formatter.format_image(alt, match.group(2))

        text = self.IMAGE_PATTERN.sub(replace_image, text)

        def replace_link(match):
            label = self.apply_inline_formatting(match.group(1), formatter)
            return formatter.format_link(label, match.group(2))

        text = self.LINK_PATTERN.sub(replace_link, text)

        text = self._apply_emphasis(text, formatter)

        def replace_strikethrough(match):
            return formatter.format_strikethrough(match.group(1))

        text = self.STRIKETHROUGH_PATTERN.sub(replace_strikethrough, text)

        def replace_emoji(match):
            return formatter.format_emoji(match.group(1))

        text = self.EMOJI_PATTERN.sub(replace_emoji, text)

        for index, formatted_code in enumerate(code_spans):
            text = text.replace(f"\x00{index}\x00", formatted_code)

        return text

    def _apply_emphasis(self, text, formatter):
        """Format bold/italic, including nested emphasis."""
        def replace_bold_italic(match):
            return formatter.format_bold(formatter.format_italic(match.group(1)))

        text = self.BOLD_ITALIC_PATTERN.sub(replace_bold_italic, text)

        def replace_nested_bold(match):
            inner = self._apply_emphasis(match.group(1), formatter)
            return formatter.format_bold(inner)

        text = self.BOLD_NESTED_PATTERN.sub(replace_nested_bold, text)

        def replace_nested_italic(match):
            inner = self._apply_emphasis(match.group(1), formatter)
            return formatter.format_italic(inner)

        text = self.ITALIC_NESTED_PATTERN.sub(replace_nested_italic, text)

        def replace_bold(match):
            return formatter.format_bold(match.group(1))

        text = self.BOLD_PATTERN.sub(replace_bold, text)

        def replace_italic(match):
            return formatter.format_italic(match.group(1))

        text = self.ITALIC_PATTERN.sub(replace_italic, text)

        return text
