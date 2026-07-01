"""
Tests for color utilities
"""

from markrender.colors import (
    Colors, rgb, rgb_bg, hex_to_rgb, colorize, get_terminal_width
)


class TestColors:
    """Test cases for Colors class"""

    def test_reset_code(self):
        """Test reset escape code"""
        assert Colors.RESET == '\033[0m'

    def test_basic_colors_exist(self):
        """Test all basic colors exist"""
        assert Colors.BLACK is not None
        assert Colors.RED is not None
        assert Colors.GREEN is not None
        assert Colors.YELLOW is not None
        assert Colors.BLUE is not None
        assert Colors.MAGENTA is not None
        assert Colors.CYAN is not None
        assert Colors.WHITE is not None

    def test_bright_colors_exist(self):
        """Test all bright colors exist"""
        assert Colors.BRIGHT_BLACK is not None
        assert Colors.BRIGHT_RED is not None
        assert Colors.BRIGHT_GREEN is not None
        assert Colors.BRIGHT_YELLOW is not None
        assert Colors.BRIGHT_BLUE is not None
        assert Colors.BRIGHT_MAGENTA is not None
        assert Colors.BRIGHT_CYAN is not None
        assert Colors.BRIGHT_WHITE is not None

    def test_background_colors_exist(self):
        """Test all background colors exist"""
        assert Colors.BG_BLACK is not None
        assert Colors.BG_RED is not None
        assert Colors.BG_GREEN is not None
        assert Colors.BG_YELLOW is not None
        assert Colors.BG_BLUE is not None
        assert Colors.BG_MAGENTA is not None
        assert Colors.BG_CYAN is not None
        assert Colors.BG_WHITE is not None
        assert Colors.BG_BRIGHT_BLACK is not None

    def test_text_styles_exist(self):
        """Test all text styles exist"""
        assert Colors.BOLD is not None
        assert Colors.DIM is not None
        assert Colors.ITALIC is not None
        assert Colors.UNDERLINE is not None

    def test_bold_code(self):
        """Test bold escape code"""
        assert Colors.BOLD == '\033[1m'

    def test_italic_code(self):
        """Test italic escape code"""
        assert Colors.ITALIC == '\033[3m'


class TestRgb:
    """Test cases for rgb function"""

    def test_rgb_returns_string(self):
        """Test rgb returns a string"""
        result = rgb(255, 0, 0)
        assert isinstance(result, str)

    def test_rgb_red(self):
        """Test rgb red"""
        result = rgb(255, 0, 0)
        assert result == '\033[38;2;255;0;0m'

    def test_rgb_green(self):
        """Test rgb green"""
        result = rgb(0, 255, 0)
        assert result == '\033[38;2;0;255;0m'

    def test_rgb_blue(self):
        """Test rgb blue"""
        result = rgb(0, 0, 255)
        assert result == '\033[38;2;0;0;255m'

    def test_rgb_black(self):
        """Test rgb black"""
        result = rgb(0, 0, 0)
        assert result == '\033[38;2;0;0;0m'

    def test_rgb_white(self):
        """Test rgb white"""
        result = rgb(255, 255, 255)
        assert result == '\033[38;2;255;255;255m'

    def test_rgb_mid(self):
        """Test rgb mid values"""
        result = rgb(128, 64, 192)
        assert result == '\033[38;2;128;64;192m'


class TestRgbBg:
    """Test cases for rgb_bg function"""

    def test_rgb_bg_returns_string(self):
        """Test rgb_bg returns a string"""
        result = rgb_bg(255, 0, 0)
        assert isinstance(result, str)

    def test_rgb_bg_red(self):
        """Test rgb_bg red"""
        result = rgb_bg(255, 0, 0)
        assert result == '\033[48;2;255;0;0m'

    def test_rgb_bg_black(self):
        """Test rgb_bg black"""
        result = rgb_bg(0, 0, 0)
        assert result == '\033[48;2;0;0;0m'


class TestHexToRgb:
    """Test cases for hex_to_rgb function"""

    def test_hex_to_rgb_red(self):
        """Test hex_to_rgb with red"""
        result = hex_to_rgb('#FF0000')
        assert result == (255, 0, 0)

    def test_hex_to_rgb_green(self):
        """Test hex_to_rgb with green"""
        result = hex_to_rgb('#00FF00')
        assert result == (0, 255, 0)

    def test_hex_to_rgb_blue(self):
        """Test hex_to_rgb with blue"""
        result = hex_to_rgb('#0000FF')
        assert result == (0, 0, 255)

    def test_hex_to_rgb_no_hash(self):
        """Test hex_to_rgb without # prefix"""
        result = hex_to_rgb('FF0000')
        assert result == (255, 0, 0)

    def test_hex_to_rgb_black(self):
        """Test hex_to_rgb with black"""
        result = hex_to_rgb('#000000')
        assert result == (0, 0, 0)

    def test_hex_to_rgb_white(self):
        """Test hex_to_rgb with white"""
        result = hex_to_rgb('#FFFFFF')
        assert result == (255, 255, 255)

    def test_hex_to_rgb_custom(self):
        """Test hex_to_rgb with custom color"""
        result = hex_to_rgb('#1E90FF')
        assert result == (30, 144, 255)


class TestColorize:
    """Test cases for colorize function"""

    def test_colorize_wraps_text(self):
        """Test colorize wraps text with color codes"""
        result = colorize("hello", Colors.RED)
        # When not in a TTY, should return plain text
        assert isinstance(result, str)

    def test_colorize_non_empty(self):
        """Test colorize returns non-empty string"""
        result = colorize("hello", Colors.RED)
        assert len(result) > 0


class TestGetTerminalWidth:
    """Test cases for get_terminal_width function"""

    def test_get_terminal_width_returns_int(self):
        """Test get_terminal_width returns integer"""
        width = get_terminal_width()
        assert isinstance(width, int)

    def test_get_terminal_width_positive(self):
        """Test get_terminal_width returns positive number"""
        width = get_terminal_width()
        assert width > 0

    def test_get_terminal_width_reasonable(self):
        """Test get_terminal_width returns reasonable value"""
        width = get_terminal_width()
        assert width >= 20
        assert width <= 500
