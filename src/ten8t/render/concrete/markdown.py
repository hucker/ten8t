"""
GitHub Markdown Ten8t Output Renderer

This adds support for handling some color coding that github allows.
"""

from ten8t.render._base import Ten8tAbstractRenderer
from ten8t.render._markup import *


class Ten8tBasicMarkdownRenderer(Ten8tAbstractRenderer):
    """
    GitHub Markdown renderer that extends basic markdown with GitHub-specific features.
    GitHub Markdown supports HTML-based color styling and other GitHub-specific features.
    """

    def __init__(self):
        super().__init__()
        self.renderer_name = "markdown"
        self.file_extensions = [".md", ".markdown"]
        self.default_extension = ".md"

        # Override and extend tag mappings with GitHub Markdown features
        self.tag_mappings = {
            TAG_BOLD: ('**', '**'),
            TAG_ITALIC: ('*', '*'),
            TAG_STRIKETHROUGH: ('~~', '~~'),
            TAG_UNDERLINE: ('<u>', '</u>'),

            TAG_PASS: ('`', '`'),
            TAG_FAIL: ('`', '`'),
            TAG_WARN: ('`', '`'),
            TAG_SKIP: ('`', '`'),
            TAG_EXPECTED: ('`', '`'),
            TAG_ACTUAL: ('`', '`'),

            # Better code formatting using GitHub syntax highlighting
            TAG_CODE: ('`', '`'),
            TAG_DATA: ('`', '`'),
        }
