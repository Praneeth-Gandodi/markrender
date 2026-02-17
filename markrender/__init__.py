"""
MarkRender - Professional Terminal Markdown Renderer

A production-ready library for rendering streaming LLM markdown responses
in terminals with beautiful syntax highlighting and formatting.
"""

__version__ = '1.0.4'
__author__ = 'Praneeth Gandodi'

from .renderer import MarkdownRenderer
from .themes import register_theme, list_themes, get_theme
from .config import create_default_config

__all__ = [
    'MarkdownRenderer',
    'register_theme',
    'list_themes',
    'get_theme',
    'create_default_config',
]
