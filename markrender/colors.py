"""
ANSI color utilities for terminal output
Python 3.7+ compatible
"""

import re
import sys


_force_color = False
_dim_mode = False


def set_force_color(val):
    global _force_color
    _force_color = val


def set_dim_mode(val):
    global _dim_mode
    _dim_mode = val


def get_force_color():
    return _force_color


def get_dim_mode():
    return _dim_mode


class Colors:
    """ANSI color codes"""
    # Reset
    RESET = '\033[0m'
    
    # Basic colors
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    
    # Bright colors
    BRIGHT_BLACK = '\033[90m'
    BRIGHT_RED = '\033[91m'
    BRIGHT_GREEN = '\033[92m'
    BRIGHT_YELLOW = '\033[93m'
    BRIGHT_BLUE = '\033[94m'
    BRIGHT_MAGENTA = '\033[95m'
    BRIGHT_CYAN = '\033[96m'
    BRIGHT_WHITE = '\033[97m'
    
    # Background colors
    BG_BLACK = '\033[40m'
    BG_RED = '\033[41m'
    BG_GREEN = '\033[42m'
    BG_YELLOW = '\033[43m'
    BG_BLUE = '\033[44m'
    BG_MAGENTA = '\033[45m'
    BG_CYAN = '\033[46m'
    BG_WHITE = '\033[47m'
    BG_BRIGHT_BLACK = '\033[100m'
    
    # Text styles
    BOLD = '\033[1m'
    DIM = '\033[2m'
    ITALIC = '\033[3m'
    UNDERLINE = '\033[4m'


def rgb(r, g, b):
    """
    Create 24-bit RGB color code
    
    Args:
        r: Red value (0-255)
        g: Green value (0-255)
        b: Blue value (0-255)
    
    Returns:
        ANSI color code string
    """
    return f'\033[38;2;{r};{g};{b}m'


def rgb_bg(r, g, b):
    """
    Create 24-bit RGB background color code
    
    Args:
        r: Red value (0-255)
        g: Green value (0-255)
        b: Blue value (0-255)
    
    Returns:
        ANSI background color code string
    """
    return f'\033[48;2;{r};{g};{b}m'


def hex_to_rgb(hex_color):
    """
    Convert hex color to RGB tuple
    
    Args:
        hex_color: Hex color string (e.g., '#FF0000' or 'FF0000')
    
    Returns:
        Tuple of (r, g, b) values
    
    Raises:
        ValueError: If hex_color is not a valid hex color string
        TypeError: If hex_color is not a string
    """
    if not isinstance(hex_color, str):
        raise TypeError(f'Expected str, got {type(hex_color).__name__}')
    hex_color = hex_color.lstrip('#')
    if len(hex_color) != 6:
        raise ValueError(f'Invalid hex color: {hex_color!r}')
    try:
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    except ValueError:
        raise ValueError(f'Invalid hex color: {hex_color!r}')


def colorize(text, color_code, force_color=None, dim_mode=None):
    if not supports_color(force_color=force_color):
        return text
    _dim = dim_mode if dim_mode is not None else _dim_mode
    prefix = Colors.DIM + color_code if _dim else color_code
    return f'{prefix}{text}{Colors.RESET}'


def supports_color(force_color=None):
    fc = force_color if force_color is not None else _force_color
    if fc:
        return True
    if not hasattr(sys.stdout, 'isatty') or not sys.stdout.isatty():
        return False
    if sys.platform == 'win32':
        try:
            import ctypes
            kernel32 = ctypes.windll.kernel32
            mode = ctypes.c_ulong()
            handle = kernel32.GetStdHandle(-11)
            if handle == 0 or handle == -1:
                return False
            if not kernel32.GetConsoleMode(handle, ctypes.byref(mode)):
                return False
            mode.value |= 0x0004
            kernel32.SetConsoleMode(handle, mode.value)
            return True
        except Exception:
            return False
    return True


def get_terminal_width():
    """
    Get terminal width
    
    Returns:
        Terminal width in characters (default 80)
    """
    try:
        import shutil
        return shutil.get_terminal_size().columns
    except Exception:
        return 80


_ANSI_PATTERN = re.compile(r'\033\[[0-9;]*[a-zA-Z]|\033\][0-9;]*[a-zA-Z].*?(\033\\|[\a])|[\x80-\x9f]')


def strip_ansi(text):
    """
    Remove ANSI escape sequences from text to prevent terminal injection.
    
    Args:
        text: Input text possibly containing ANSI escape codes
    
    Returns:
        Text with ANSI escape sequences stripped
    """
    if not isinstance(text, str):
        return text
    return _ANSI_PATTERN.sub('', text)
