"""
This file handles the Markup used by Ten8t.

The markup is a simple search and replace on tags that look like:

<<red>>Hello World<</red>>

About 20 such tags are supported.  The expectation is that the tags will be used to format
single lines of text where each line represents a test result of some kind.  Thus, all
the formatting is setting color and font.

The code requires each new formatter to provide a dictionary of mappings that it supports.
Once the mapping is provided the output from a checker run can be formatted for display in
the supported formats.

"""
from ..ten8t_exception import Ten8tValueError

# Supported HTML style tags
# Define your tags as constants
TAG_BOLD = 'b'
TAG_ITALIC = 'i'
TAG_UNDERLINE = 'u'
TAG_STRIKETHROUGH = 's'
TAG_DATA = 'data'
TAG_EXPECTED = 'expected'
TAG_ACTUAL = 'actual'
TAG_FAIL = 'fail'
TAG_PASS = 'pass'
TAG_SKIP = 'skip'
TAG_WARN = 'warn'
TAG_CODE = 'code'
TAG_RED = 'red'
TAG_BLUE = 'blue'
TAG_GREEN = 'green'
TAG_PURPLE = 'purple'
TAG_ORANGE = 'orange'
TAG_YELLOW = 'yellow'
TAG_BLACK = 'black'
TAG_WHITE = 'white'


class Ten8tMarkup:
    """
    Baseline formatter class to be used by ten8t rules.

    The idea of ten8t markup is a way to tag all result message with formatting
    information that may be used to provide the end user with a richer formatting
    experience targeting multiple output environments.  Since I use rich_ten8t, markdown
    and streamlit and a bit of HTML I needed it to work for those platforms.

    Ten8t messages can have embedded formatting information that indicates to
    higher level code how the text could be formatted.  Rendering class can choose
    what to do with the tags including doing nothing.

    The markup looks like html, with open and close tags.  This was chosen to
    make the simple search/replace algorithm have easy matches.

    The idea is that you could want a way to write a red message, so you could do:

    "Hello <<red>>world!<<red>>"

    or perhaps in code

    f"Hello {fmt.red('world!')}"

    to make your formatted output.

    If no formatter was specified, a text formatter would just run through the code
    and strip out all the <<>> tags, leaving the plain text:

    Hello world!

    A rich_ten8t formatter might replace those tags with:

    "Hello [red]world![/red]"

    Incorporating this mechanism into your code should be pretty easy.  All you need to do
    is markup your text with ANY subset of the markup and then choose a render class to
    render output to your target.  Initially you use the text render which does
    nothing but strip off all the tags, leaving you with plain text messages suitable for
    logging.

    NOTE: This markup is intended for small amounts of text.  Generally single lines of text output.
    It should be used to add some color or bold text to line based string output.  It supports many outputs
    it sort of only works well for the subset of features that every target supports.  If you target HTML
    then you should be able to do almost anything since it supports deep nesting, however if you target
    markdown you will run into issues if you try deeply nest (or even nest) some tags.

    """

    # If you don't like my delimiters pick your own.

    def __init__(self, open_pattern: str = "<<{}>>", close_pattern: str = "<</{}>>"):
        """
        Init only allows you to specify open and close delimiters.

        The assumption is that you want markup that looks like <<bold>> <</bold>> and this
        __init__ defaults to those delimiters.

        If you don't like the <<>> then you can change it.

        """
        self.open_pattern = open_pattern
        self.close_pattern = close_pattern

        if open_pattern == close_pattern:
            raise Ten8tValueError("Open and close patterns %s for markup should not be the same.", open_pattern)

    def open_tag(self, tag: str) -> str:
        """if tag is 'red' open tag is <<red>>"""
        return self.open_pattern.format(tag.strip())

    def close_tag(self, tag: str) -> str:
        """If  tag is 'red' close tag is <</red>>"""
        return self.close_pattern.format(tag.strip())

    def _tag(self, id_, msg):
        """Create a generic tag string like <<code>>x=1<</code>>"""
        return f'{self.open_tag(id_)}{msg}{self.close_tag(id_)}'

    def bold(self, msg):
        """Create bold tag function. """
        return self._tag('b', msg)

    def italic(self, msg):
        """Create italic tag function. """
        return self._tag('i', msg)

    def underline(self, msg):
        """Create underline tag function."""
        return self._tag('u', msg)

    def strikethrough(self, msg):
        """Create strikethrough tag function. """
        return self._tag('s', msg)

    def code(self, msg):
        """Create code tag function. """
        return self._tag('code', msg)

    def data(self, msg):
        """Create data tag function. """
        return self._tag('data', msg)

    def expected(self, msg):
        """Create expected tag function. """
        return self._tag('expected', msg)

    def actual(self, msg):
        """Create actual tag function. """
        return self._tag('actual', msg)

    def fail(self, msg):
        """Create fail tag function. """
        return self._tag('fail', msg)

    def pass_(self, msg):
        """Create pass tag function. """
        return self._tag('pass', msg)

    def warn(self, msg):
        """Create warn tag function. """
        return self._tag('warn', msg)

    def skip(self, msg):
        """Create skip tag function. """
        return self._tag('skip', msg)

    def red(self, msg):
        """Create red tag function. """
        return self._tag('red', msg)

    def blue(self, msg):
        """Create blue tag function. """
        return self._tag('blue', msg)

    def green(self, msg):
        """Create green tag function. """
        return self._tag('green', msg)

    def yellow(self, msg):
        """Create yellow tag function. """
        return self._tag('yellow', msg)

    def orange(self, msg):
        """Create orange tag function. """
        return self._tag('orange', msg)

    def purple(self, msg):
        """Create purple tag function. """
        return self._tag('purple', msg)

    def black(self, msg):
        """Create black tag function. """
        return self._tag('black', msg)

    def white(self, msg):
        """Create white tag function. """
        return self._tag('white', msg)


# Create in instance of the markup class that can easily be used.  This instance
# is a shorthand that makes writing f-strings more compact and have access to a global
# markup formatter.  I have no thought that there will be multiple markups running at
# the same time, though I can image multiple renderers running at the same time, the
# obvious example being writing to a log file and a web interface or markdown file.
BM = Ten8tMarkup()
