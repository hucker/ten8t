"""
Ten8tMarkup for Raw Text
"""

from .._base import Ten8tAbstractRenderer


class Ten8tTextRenderer(Ten8tAbstractRenderer):
    """
    GitHub Markdown renderer that extends basic markdown with GitHub-specific features.
    GitHub Markdown supports HTML-based color styling and other GitHub-specific features.
    """

    def __init__(self):
        super().__init__()
        self.renderer_name = "text"
        self.file_extensions = [".txt"]
        self.default_extension = ".txt"

        # text has no mappings so all markup is effectively stripped.
        self.tag_mappings = {}
