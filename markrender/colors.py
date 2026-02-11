"""
ANSI color utilities for terminal output
Python 3.7+ compatible
"""

import os
import sys


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
    """
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))


def colorize(text, color_code, force_color=False):
    """
    Apply color to text
    
    Args:
        text: Text to colorize
        color_code: ANSI color code
        force_color: If True, force color output regardless of terminal capabilities.
    
    Returns:
        Colorized text with reset at the end
    """
    if force_color or supports_color():
        return f'{color_code}{text}{Colors.RESET}'
    return text


def supports_color():
    """
    Check if terminal supports color output
    
    Returns:
        True if colors are supported, False otherwise
    """
    # Check if output is redirected
    if not hasattr(sys.stdout, 'isatty') or not sys.stdout.isatty():
        return False
    
    # Windows color support
    if sys.platform == 'win32':
        # Enable virtual terminal processing on Windows 10+
        try:
            import ctypes
            kernel32 = ctypes.windll.kernel32
            # Get console mode
            mode = ctypes.c_ulong()
            kernel32.GetConsoleMode(kernel32.GetStdHandle(-11), ctypes.byref(mode))
            # Enable virtual terminal processing (0x0004)
            mode.value |= 0x0004
            kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), mode.value)
            return True
        except Exception:
            # Fallback: check for Windows Terminal or other modern terminals
            return os.environ.get('WT_SESSION') or os.environ.get('TERM_PROGRAM')
    
    # Unix-like systems
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
