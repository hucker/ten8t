"""
Base class for all ten8t renderers.  This has a list of all supported tags, the abstract
render method and a concrete cleanup that removes all un-rendered tags.
"""
from abc import ABC

from ten8t.render.markup import *

# List of all known tags.  We need the list of all tags because code will need to run through all
# tags and remove them if they aren't formatted.
tags = [TAG_BOLD, TAG_ITALIC, TAG_UNDERLINE, TAG_STRIKETHROUGH, TAG_DATA, TAG_EXPECTED, TAG_ACTUAL, TAG_FAIL,
        TAG_PASS, TAG_CODE, TAG_RED, TAG_BLUE, TAG_GREEN, TAG_PURPLE, TAG_ORANGE, TAG_YELLOW, TAG_BLACK, TAG_WHITE,
        TAG_WARN, TAG_SKIP]


class Ten8tAbstractRenderer(ABC):
    """
    Base class for all ten8t renderers.  This has a list of all supported tags, the abstract
    render method and a concrete cleanup that removes all un-rendered tags.
    """

    # List of all known tags.  We need the list of all tags because code will need to run through all
    # tags and remove them if they aren't formatted.
    tags = [TAG_BOLD, TAG_ITALIC, TAG_UNDERLINE, TAG_STRIKETHROUGH, TAG_DATA, TAG_EXPECTED, TAG_ACTUAL, TAG_FAIL,
            TAG_PASS, TAG_CODE, TAG_RED, TAG_BLUE, TAG_GREEN, TAG_PURPLE, TAG_ORANGE, TAG_YELLOW, TAG_BLACK, TAG_WHITE,
            TAG_WARN, TAG_SKIP]

    def render(self, msg):
        """
        Apply tag mappings to transform markup in the message.
        Subclasses only need to define their tag_mappings dictionary.
        """
        fmt = Ten8tMarkup()

        # Replace each tag with its mapped representation
        for tag, (opening, closing) in self.tag_mappings.items():
            msg = msg.replace(fmt.open_tag(tag), opening)
            msg = msg.replace(fmt.close_tag(tag), closing)

        # Clean up any remaining tags
        msg = self.cleanup(msg)
        return msg

    def cleanup(self, msg):
        """
        It is optional for subclasses to replace all the render tags.  This method provides
        support to wipeout all un rendered tags.
        """
        fmt = Ten8tMarkup()

        # Find all the defined tags and blow them away.
        for tag in self.tags:
            msg = msg.replace(f'{fmt.open_tag(tag)}', '')
            msg = msg.replace(f'{fmt.close_tag(tag)}', '')

        return msg
