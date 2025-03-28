"""
Exports all Ten8t renderer classes from the render package.
"""

# Import base classes and protocols
from ._base import Ten8tAbstractRenderer
# Import factory
from ._factory import Ten8tRendererFactory
from ._markup import BM, Ten8tMarkup
# Import markup definitions
from ._markup import TAG_ACTUAL, TAG_BLACK, TAG_BLUE, TAG_BOLD, TAG_CODE, TAG_DATA, TAG_EXPECTED, TAG_FAIL, TAG_GREEN, \
    TAG_ITALIC, TAG_ORANGE, TAG_PASS, TAG_PURPLE, TAG_RED, TAG_SKIP, TAG_STRIKETHROUGH, TAG_UNDERLINE, TAG_WARN, \
    TAG_WHITE, TAG_YELLOW, Ten8tMarkup
from ._protocol import Ten8tRendererProtocol
# Import concrete renderers
from .concrete import (Ten8tBasicHTMLRenderer, Ten8tBasicMarkdownRenderer, Ten8tBasicRichRenderer,
                       Ten8tBasicStreamlitRenderer, Ten8tGitHubMarkdownRenderer, Ten8tTextRenderer)

# Define the public exports
__all__ = [
    # Base classes
    'Ten8tAbstractRenderer',
    'Ten8tRendererProtocol',

    # Renderers
    'Ten8tBasicHTMLRenderer',
    'Ten8tBasicMarkdownRenderer',
    'Ten8tGitHubMarkdownRenderer',
    'Ten8tBasicRichRenderer',
    'Ten8tBasicStreamlitRenderer',
    'Ten8tTextRenderer',
    'Ten8tRendererFactory',

    # Markup
    'Ten8tMarkup',
    'BM',

    # Tags
    'TAG_BOLD', 'TAG_ITALIC', 'TAG_UNDERLINE', 'TAG_STRIKETHROUGH',
    'TAG_DATA', 'TAG_EXPECTED', 'TAG_ACTUAL', 'TAG_FAIL', 'TAG_PASS',
    'TAG_CODE', 'TAG_RED', 'TAG_BLUE', 'TAG_GREEN', 'TAG_PURPLE',
    'TAG_ORANGE', 'TAG_YELLOW', 'TAG_BLACK', 'TAG_WHITE', 'TAG_WARN', 'TAG_SKIP'
]
