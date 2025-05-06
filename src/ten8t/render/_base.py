"""
Base class for all ten8t renderers.  This has a list of all supported tags, the abstract
render method and a concrete cleanup that removes all un-rendered tags.

The purpose of this class is for formatting and coloring output of test results uniformly
against many target environments (e.g., html, markdown, streamlit...)  The use case is FULLY
intended to only support formatting single lines of text for reporting purposes.

This is NOT intended to format documents as much as it meant to format lines of text.

As such there is support for coloring and font types and also the ability to format types of
information.  The Pass tag might color things green, while the FAIL tag might color things red.

This mechanism supports many output formats, so it sort of means that it hits a least
common denominator of functionality.  The main casualty of this is that nested formatting is not supported because
some targets don't support nesting.  This doesn't mean you couldn't set up nesting IF you know your
target will support it (HTML for example), but in doing so your output will not be able to be displayed
in targets that can't do nesting.

Please refer to _markup.py for a list of the supported tags and information on how to use them.

"""
from abc import ABC

from ten8t.render._markup import *


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

    # This has all the markups that ten8t knows about, these shouldn't change
    markup = Ten8tMarkup()

    # Used by factory
    renderer_name = "base"

    def __init__(self):

        # Subclasses only need to fill in this mapping.
        self.tag_mappings = {}

    def render(self, msg):
        """
        Apply tag mappings to transform markup in the message.
        Subclasses only need to define their tag_mappings dictionary.
        """

        # Replace each tag with its mapped representation such as:
        # <<code>>"hello"<</code>> -> `code`
        for tag, (opening, closing) in self.tag_mappings.items():
            msg = msg.replace(self.markup.open_tag(tag), opening)
            msg = msg.replace(self.markup.close_tag(tag), closing)

        # Clean up any remaining tags
        msg = self.cleanup(msg)
        return msg

    def cleanup(self, msg):
        """
        It is optional for subclasses to replace all the render tags.  This method provides
        support to wipeout all un rendered tags.
        """

        # Find all the defined tags and blow them away.
        for tag in self.tags:
            msg = msg.replace(f'{self.markup.open_tag(tag)}', '')
            msg = msg.replace(f'{self.markup.close_tag(tag)}', '')

        return msg
