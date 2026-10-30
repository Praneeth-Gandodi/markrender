"""
MarkRender - Professional Terminal Markdown Renderer

A production-ready library for rendering streaming LLM markdown responses
in terminals with beautiful syntax highlighting and formatting.
"""

try:
    from ._version import __version__
except ImportError:  # Running from a source checkout without a build.
    try:
        from importlib.metadata import version as _installed_version

        __version__ = _installed_version("markrender")
    except Exception:
        __version__ = "0.0.0+unknown"

__author__ = 'Praneeth Gandodi'

from .renderer import MarkdownRenderer

__all__ = ['MarkdownRenderer']
