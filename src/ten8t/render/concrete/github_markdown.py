"""
GitHub Markdown Ten8t Output Renderer

This adds support for handling some color coding that github allows.
"""

from ten8t.render._base import Ten8tAbstractRenderer
from ten8t.render._markup import *


class Ten8tGitHubMarkdownRenderer(Ten8tAbstractRenderer):
    """
    GitHub Markdown renderer that extends basic markdown with GitHub-specific features.
    GitHub Markdown supports HTML-based color styling and other GitHub-specific features.
    """


    def __init__(self):
        super().__init__()
        self.renderer_name = "github_markdown"
        self.file_extensions = [".md",".markdown",".gfm"]
        self.default_extension = ".gfm"

        # Override and extend tag mappings with GitHub Markdown features
        self.tag_mappings = {
            TAG_BOLD: ('**', '**'),
            TAG_ITALIC: ('*', '*'),
            TAG_STRIKETHROUGH: ('~~', '~~'),
            TAG_UNDERLINE: ('<u>', '</u>'),  # HTML tags for underline since Markdown doesn't have native underline

            # Color tags using GitHub Markdown color syntax (via HTML)
            TAG_RED: ('<span style="color:red">', '</span>'),
            TAG_GREEN: ('<span style="color:green">', '</span>'),
            TAG_BLUE: ('<span style="color:blue">', '</span>'),
            TAG_YELLOW: ('<span style="color:yellow">', '</span>'),
            TAG_ORANGE: ('<span style="color:orange">', '</span>'),
            TAG_PURPLE: ('<span style="color:purple">', '</span>'),
            TAG_BLACK: ('<span style="color:black">', '</span>'),
            TAG_WHITE: ('<span style="color:white">', '</span>'),

            # Status tags with more distinctive styling
            TAG_PASS: ('<span style="color:green; font-weight:bold">', '</span>'),
            TAG_FAIL: ('<span style="color:red; font-weight:bold">', '</span>'),
            TAG_WARN: ('<span style="color:orange; font-weight:bold">', '</span>'),
            TAG_SKIP: ('<span style="color:blue; font-weight:bold">', '</span>'),

            # Add better styling for expected/actual
            TAG_EXPECTED: ('<span style="color:green">Expected: ', '</span>'),
            TAG_ACTUAL: ('<span style="color:green">Actual: ', '</span>'),

            # Better code formatting using GitHub syntax highlighting
            TAG_CODE: ('<code>', '</code>'),  #('```python\n', '\n```'),
            TAG_DATA: ('<code>', '</code>'),
        }
