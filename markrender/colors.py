"""
ANSI color utilities for terminal output
Python 3.7+ compatible
"""

import os
import sys
import colorama

colorama.init()

# Define common rich styles based on ANSI codes
# Rich understands these string representations directly
RICH_STYLES = {
    'BLACK': 'black', 'RED': 'red', 'GREEN': 'green', 'YELLOW': 'yellow',
    'BLUE': 'blue', 'MAGENTA': 'magenta', 'CYAN': 'cyan', 'WHITE': 'white',
    
    'BRIGHT_BLACK': 'bright_black', 'BRIGHT_RED': 'bright_red', 'BRIGHT_GREEN': 'bright_green',
    'BRIGHT_YELLOW': 'bright_yellow', 'BRIGHT_BLUE': 'bright_blue', 'BRIGHT_MAGENTA': 'bright_magenta',
    'BRIGHT_CYAN': 'bright_cyan', 'BRIGHT_WHITE': 'bright_white',
    
    'BG_BLACK': 'on black', 'BG_RED': 'on red', 'BG_GREEN': 'on green', 'BG_YELLOW': 'on yellow',
    'BG_BLUE': 'on blue', 'BG_MAGENTA': 'on magenta', 'BG_CYAN': 'on cyan', 'BG_WHITE': 'on white',
    'BG_BRIGHT_BLACK': 'on bright_black', # Rich doesn't have direct 'on bright black', so using similar
    
    'BOLD': 'bold', 'DIM': 'dim', 'ITALIC': 'italic', 'UNDERLINE': 'underline',
    'RESET': 'not bold not dim not italic not underline not reverse not strike' # A comprehensive reset
}

class Colors:
    """ANSI color codes - kept for compatibility/mapping"""
    RESET = '\033[0m'
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    
    BRIGHT_BLACK = '\033[90m'
    BRIGHT_RED = '\033[91m'
    BRIGHT_GREEN = '\033[92m'
    BRIGHT_YELLOW = '\033[93m'
    BRIGHT_BLUE = '\033[94m'
    BRIGHT_MAGENTA = '\033[95m'
    BRIGHT_CYAN = '\033[96m'
    BRIGHT_WHITE = '\033[97m'
    
    BG_BLACK = '\033[40m'
    BG_RED = '\033[41m'
    BG_GREEN = '\033[42m'
    BG_YELLOW = '\033[43m'
    BG_BLUE = '\033[44m'
    BG_MAGENTA = '\033[45m'
    BG_CYAN = '\033[46m'
    BG_WHITE = '\033[47m'
    BG_BRIGHT_BLACK = '\033[100m'
    
    BOLD = '\033[1m'
    DIM = '\033[2m'
    ITALIC = '\033[3m'
    UNDERLINE = '\033[4m'


def get_rich_color_style(ansi_color_code, is_background=False):
    """
    Translates an ANSI color code to a rich compatible style string.
    """
    if ansi_color_code == Colors.RESET:
        return RICH_STYLES['RESET']
    
    # Check if it's already a valid Rich style string (or close to it)
    if isinstance(ansi_color_code, str):
        if ansi_color_code.startswith('#') or ansi_color_code.startswith('rgb(') or ansi_color_code in RICH_STYLES.values():
            return ansi_color_code

    # Simple mapping for basic colors
    for name, code in Colors.__dict__.items():
        if isinstance(code, str) and code == ansi_color_code:
            rich_style_name = name
            if is_background:
                if name.startswith('BG_'):
                    return RICH_STYLES.get(name)
                else: # Try to find corresponding BG style
                    bg_name = f'BG_{name}'
                    return RICH_STYLES.get(bg_name)
            else:
                return RICH_STYLES.get(name)

    # For RGB/24-bit colors
    if isinstance(ansi_color_code, str):
        if ansi_color_code.startswith('\033[38;2;'): # Foreground RGB
            parts = ansi_color_code.split(';')
            if len(parts) >= 5:
                r, g, b = parts[2], parts[3], parts[4].rstrip('m')
                return f'rgb({r},{g},{b})'
        elif ansi_color_code.startswith('\033[48;2;'): # Background RGB
            parts = ansi_color_code.split(';')
            if len(parts) >= 5:
                r, g, b = parts[2], parts[3], parts[4].rstrip('m')
                return f'on rgb({r},{g},{b})'
        
        # Fallback: looks like a color name
        if not ansi_color_code.startswith('\033'):
            return ansi_color_code
            
    return None # Fallback if no mapping found


def rgb(r, g, b):
    """
    Create 24-bit RGB color code
    """
    return f'\033[38;2;{r};{g};{b}m'


def rgb_bg(r, g, b):
    """
    Create 24-bit RGB background color code
    """
    return f'\033[48;2;{r};{g};{b}m'


def hex_to_rgb(hex_color):
    """
    Convert hex color to RGB tuple
    """
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))


def colorize(text, color_code, force_color=False, rich_text=None):
    """
    Apply color to text. Can return ANSI string or apply to rich.Text.
    """
    if rich_text is not None and rich_available: # If rich_text object is provided
        rich_style = get_rich_color_style(color_code)
        if rich_style:
            rich_text.stylize(rich_style, 0, len(text))
        return rich_text
    
    # Fallback to ANSI string if rich not available or rich_text not requested
    if force_color or (hasattr(sys.stdout, 'isatty') and sys.stdout.isatty()):
        return f'{color_code}{text}{Colors.RESET}'
    return text


def get_terminal_width():
    """
    Get terminal width
    """
    try:
        import shutil
        return shutil.get_terminal_size().columns
    except Exception:
        return 80
