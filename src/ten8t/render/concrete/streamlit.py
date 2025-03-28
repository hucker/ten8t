from .._base import *


class Ten8tBasicStreamlitRenderer(Ten8tAbstractRenderer):
    """Streamlit renderer class."""

    def __init__(self):
        super().__init__()
        self.renderer_name = "streamlit"
        self.file_extensions = []
        self.default_extension = ''

        # text has no mappings so all markup is effectively stripped.
        self.tag_mappings = {
            TAG_BOLD: ('**', '**'),
            TAG_ITALIC: ('*', '*'),
            TAG_CODE: ('`', '`'),
            TAG_PASS: (':green[', ']'),
            TAG_FAIL: (':red[', ']'),
            TAG_WARN: (':orange[', ']'),
            TAG_SKIP: (':purple[', ']'),
            TAG_EXPECTED: (':green[', ']'),
            TAG_ACTUAL: (':green[', ']'),
            TAG_RED: (':red[', ']'),
            TAG_GREEN: (':green[', ']'),
            TAG_BLUE: (':blue[', ']'),
            TAG_YELLOW: (':yellow[', ']'),
            TAG_ORANGE: (':orange[', ']'),
            TAG_PURPLE: (':purple[', ']'),
            TAG_WHITE: (':white[', ']'),
        }
