"""
Theme definitions for syntax highlighting and markdown elements
"""

from .colors import rgb, Colors


# Syntax highlighting themes for code blocks
SYNTAX_THEMES = {
    'github-dark': {
        'name': 'github-dark',
        'pygments_style': 'monokai',  # Close approximation
        'heading_colors': {
            1: rgb(88, 166, 255),   # Bright blue
            2: rgb(121, 192, 255),  # Light blue
            3: rgb(150, 203, 254),  # Lighter blue
            4: rgb(180, 215, 253),  # Very light blue
            5: rgb(200, 225, 252),  # Pale blue
            6: rgb(220, 235, 251),  # Very pale blue
        },
        'inline_code': rgb(201, 158, 255),  # Purple variant
        'link': rgb(88, 166, 255),
        'blockquote_border': Colors.BRIGHT_BLACK,
        'table_border': Colors.BRIGHT_BLACK,
        'checkbox_unchecked': Colors.BRIGHT_BLACK,
        'checkbox_checked': rgb(46, 160, 67),  # Green
        'hr': Colors.BRIGHT_BLACK,
        'note_color': rgb(229, 192, 123),
        'list_marker': rgb(88, 166, 255),
        'table_header': rgb(88, 166, 255),
        'highlight': rgb(255, 255, 0),  # Yellow for highlight
    },
    'monokai': {
        'name': 'monokai',
        'pygments_style': 'monokai',
        'heading_colors': {
            1: rgb(249, 38, 114),   # Pink
            2: rgb(102, 217, 239),  # Cyan
            3: rgb(166, 226, 46),   # Green
            4: rgb(253, 151, 31),   # Orange
            5: rgb(174, 129, 255),  # Purple
            6: rgb(230, 219, 116),  # Yellow
        },
        'inline_code': rgb(174, 129, 255),
        'link': rgb(102, 217, 239),
        'blockquote_border': rgb(117, 113, 94),
        'table_border': rgb(117, 113, 94),
        'checkbox_unchecked': rgb(117, 113, 94),
        'checkbox_checked': rgb(166, 226, 46),
        'hr': rgb(117, 113, 94),
        'note_color': rgb(230, 219, 116),
        'list_marker': rgb(102, 217, 239),  # Cyan
        'table_header': rgb(249, 38, 114),  # Pink
        'highlight': rgb(230, 219, 116),  # Yellow for highlight
    },
    'dracula': {
        'name': 'dracula',
        'pygments_style': 'dracula',
        'heading_colors': {
            1: rgb(255, 121, 198),  # Pink
            2: rgb(189, 147, 249),  # Purple
            3: rgb(139, 233, 253),  # Cyan
            4: rgb(80, 250, 123),   # Green
            5: rgb(255, 184, 108),  # Orange
            6: rgb(241, 250, 140),  # Yellow
        },
        'inline_code': rgb(189, 147, 249),
        'link': rgb(139, 233, 253),
        'blockquote_border': rgb(98, 114, 164),
        'table_border': rgb(98, 114, 164),
        'checkbox_unchecked': rgb(98, 114, 164),
        'checkbox_checked': rgb(80, 250, 123),
        'hr': rgb(98, 114, 164),
        'note_color': rgb(241, 250, 140),
        'list_marker': rgb(189, 147, 249),  # Purple
        'table_header': rgb(255, 121, 198),  # Pink
        'highlight': rgb(241, 250, 140),  # Yellow for highlight
    },
    'nord': {
        'name': 'nord',
        'pygments_style': 'nord',
        'heading_colors': {
            1: rgb(136, 192, 208),  # Frost blue
            2: rgb(129, 161, 193),  # Lighter blue
            3: rgb(94, 129, 172),   # Blue
            4: rgb(143, 188, 187),  # Teal
            5: rgb(163, 190, 140),  # Green
            6: rgb(191, 97, 106),   # Red
        },
        'inline_code': rgb(180, 142, 173),
        'link': rgb(136, 192, 208),
        'blockquote_border': rgb(76, 86, 106),
        'table_border': rgb(76, 86, 106),
        'checkbox_unchecked': rgb(76, 86, 106),
        'checkbox_checked': rgb(163, 190, 140),
        'hr': rgb(76, 86, 106),
        'note_color': rgb(235, 203, 139),
        'list_marker': rgb(136, 192, 208),  # Frost blue
        'table_header': rgb(136, 192, 208),
        'highlight': rgb(235, 203, 139),  # Yellow for highlight
    },
    'one-dark': {
        'name': 'one-dark',
        'pygments_style': 'one-dark',
        'heading_colors': {
            1: rgb(224, 108, 117),  # Red
            2: rgb(209, 154, 102),  # Orange
            3: rgb(229, 192, 123),  # Yellow
            4: rgb(152, 195, 121),  # Green
            5: rgb(86, 182, 194),   # Cyan
            6: rgb(97, 175, 239),   # Blue
        },
        'inline_code': rgb(198, 120, 221),
        'link': rgb(97, 175, 239),
        'blockquote_border': rgb(92, 99, 112),
        'table_border': rgb(92, 99, 112),
        'checkbox_unchecked': rgb(92, 99, 112),
        'checkbox_checked': rgb(152, 195, 121),
        'hr': rgb(92, 99, 112),
        'note_color': rgb(229, 192, 123),
        'list_marker': rgb(97, 175, 239),
        'table_header': rgb(224, 108, 117),
        'highlight': rgb(229, 192, 123),  # Yellow for highlight
    },
    'solarized-dark': {
        'name': 'solarized-dark',
        'pygments_style': 'solarized-dark',
        'heading_colors': {
            1: rgb(38, 139, 210),   # Blue
            2: rgb(42, 161, 152),   # Cyan
            3: rgb(133, 153, 0),    # Green
            4: rgb(181, 137, 0),    # Yellow
            5: rgb(203, 75, 22),    # Orange
            6: rgb(211, 54, 130),   # Magenta
        },
        'inline_code': rgb(108, 113, 196),
        'link': rgb(38, 139, 210),
        'blockquote_border': rgb(88, 110, 117),
        'table_border': rgb(88, 110, 117),
        'checkbox_unchecked': rgb(88, 110, 117),
        'checkbox_checked': rgb(133, 153, 0),
        'hr': rgb(88, 110, 117),
        'note_color': rgb(181, 137, 0),
        'list_marker': rgb(38, 139, 210),
        'table_header': rgb(133, 153, 0),
        'highlight': rgb(181, 137, 0),  # Yellow for highlight
    },
    'solarized-light': {
        'name': 'solarized-light',
        'pygments_style': 'solarized-light',
        'heading_colors': {
            1: rgb(38, 139, 210),   # Blue
            2: rgb(42, 161, 152),   # Cyan
            3: rgb(133, 153, 0),    # Green
            4: rgb(181, 137, 0),    # Yellow
            5: rgb(203, 75, 22),    # Orange
            6: rgb(211, 54, 130),   # Magenta
        },
        'inline_code': rgb(108, 113, 196),
        'link': rgb(38, 139, 210),
        'blockquote_border': rgb(147, 161, 161),
        'table_border': rgb(147, 161, 161),
        'checkbox_unchecked': rgb(147, 161, 161),
        'checkbox_checked': rgb(133, 153, 0),
        'hr': rgb(147, 161, 161),
        'note_color': rgb(181, 137, 0),
        'list_marker': rgb(38, 139, 210),
        'table_header': rgb(133, 153, 0),
        'highlight': rgb(181, 137, 0),  # Yellow for highlight
    },
}


def get_theme(theme_name):
    """
    Get theme configuration by name
    
    Args:
        theme_name: Name of the theme
    
    Returns:
        Theme dictionary
    
    Raises:
        ValueError: If theme doesn't exist
    """
    if theme_name not in SYNTAX_THEMES:
        available = ', '.join(SYNTAX_THEMES.keys())
        raise ValueError(f"Theme '{theme_name}' not found. Available themes: {available}")
    return SYNTAX_THEMES[theme_name]


def list_themes():
    """
    Get list of available theme names

    Returns:
        List of theme names
    """
    return list(SYNTAX_THEMES.keys())


def register_theme(name, theme_config):
    """
    Register a custom theme.
    
    Args:
        name: Theme name
        theme_config: Theme configuration dictionary with keys:
            - name: Theme display name
            - pygments_style: Pygments style name
            - heading_colors: Dict mapping level (1-6) to colors
            - inline_code: Color for inline code
            - link: Color for links
            - blockquote_border: Color for blockquote borders
            - table_border: Color for table borders
            - checkbox_unchecked: Color for unchecked checkboxes
            - checkbox_checked: Color for checked checkboxes
            - hr: Color for horizontal rules
            - highlight: Color for highlighted text
            - list_marker: Color for list markers
            - table_header: Color for table headers
            
    Example:
        register_theme('my-theme', {
            'name': 'my-theme',
            'pygments_style': 'monokai',
            'heading_colors': {1: '#ff0000', ...},
            'inline_code': '#00ff00',
            'link': '#0000ff',
            ...
        })
    """
    SYNTAX_THEMES[name] = theme_config
