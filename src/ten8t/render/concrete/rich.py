from .._base import *


class Ten8tBasicRichRenderer(Ten8tAbstractRenderer):
    """Rich render class"""

    def __init__(self):
        super().__init__()
        self.renderer_name = "rich"
        self.file_extensions = []
        self.default_extension = ''

        # text has no mappings so all markup is effectively stripped.
        self.tag_mappings = {TAG_BOLD: ('[bold]', '[/bold]'),
                             TAG_ITALIC: ('[italic]', '[/italic]'),
                             TAG_UNDERLINE: ('[u]', '[/u]'),
                             TAG_STRIKETHROUGH: ('[strike]', '[/strike]'),
                             TAG_CODE: ('[bold]', '[/bold]'),
                             TAG_PASS: ('[green]', '[/green]'),
                             TAG_FAIL: ('[red]', '[/red]'),
                             TAG_WARN: ('[orange]', '[/orange]'),
                             TAG_SKIP: ('[purple]', '[/purple]'),
                             TAG_EXPECTED: ('[green]', '[/green]'),
                             TAG_ACTUAL: ('[green]', '[/green]'),
                             TAG_RED: ('[red]', '[/red]'),
                             TAG_GREEN: ('[green]', '[/green]'),
                             TAG_BLUE: ('[blue]', '[/blue]'),
                             TAG_YELLOW: ('[yellow]', '[/yellow]'),
                             TAG_ORANGE: ('[orange]', '[/orange]'),
                             TAG_PURPLE: ('[purple]', '[/purple]'),
                             TAG_BLACK: ('[black]', '[/black]'),
                             TAG_WHITE: ('[white]', '[/white]'),
                             }
