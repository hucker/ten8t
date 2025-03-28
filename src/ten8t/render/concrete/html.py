"""
GitHub Markdown Ten8t Output Renderer

This adds support for handling some color coding that github allows.
"""

from ten8t.render._base import Ten8tAbstractRenderer
from ten8t.render._markup import *


class Ten8tBasicHTMLRenderer(Ten8tAbstractRenderer):
    """
    Simple HTML renderer.
    """

    def __init__(self):
        super().__init__()
        self.renderer_name = "html"
        self.file_extensions = [".html", ".htm"]
        self.default_extension = ".html"

        # Override and extend tag mappings with GitHub Markdown features
        self.tag_mappings = {
            TAG_BOLD: ("<b>", "</b>"),
            TAG_ITALIC: ("<i>", "</i>"),
            TAG_UNDERLINE: ("<u>", "</u>"),
            TAG_STRIKETHROUGH: ("<s>", "</s>"),
            TAG_CODE: ("<code>", "</code>"),
            TAG_PASS: ('<span style="color:green">', "</span>"),
            TAG_FAIL: ('<span style="color:red">', "</span>"),
            TAG_WARN: ('<span style="color:orange">', "</span>"),
            TAG_SKIP: ('<span style="color:purple">', "</span>"),
            TAG_EXPECTED: ('<span style="color:green">', "</span>"),
            TAG_ACTUAL: ('<span style="color:red">', "</span>"),
            TAG_RED: ('<span style="color:red">', "</span>"),
            TAG_GREEN: ('<span style="color:green">', "</span>"),
            TAG_BLUE: ('<span style="color:blue">', "</span>"),
            TAG_YELLOW: ('<span style="color:yellow">', "</span>"),
            TAG_ORANGE: ('<span style="color:orange">', "</span>"),
            TAG_PURPLE: ('<span style="color:purple">', "</span>"),
            TAG_BLACK: ('<span style="color:black">', "</span>"),
            TAG_WHITE: ('<span style="color:white">', "</span>"),
        }
