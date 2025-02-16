"""
Classes to support formatting result output.

It is assumed the output from ten8t will be used in different contexts, command line, web, markdown etc.  
As such, this class generalizes the output of ten8t's messages.

Blink message may use Ten8tMarkup to format them.  In most cases the raw text is sufficient, but there
are instances were nicer output is desired or required.

In order to accomplish this, the Ten8tMarkup class allows a very simple formatting of the messages.  THis
markup may be rendered in various ways dependent upon the message formatting.  This code provides basic markdown
that looks similar to HTML.

You can just write the markdown in your messages, or you can use the Ten8tMarkup class to generate
the inline text. 

The default formatting is plain text, which effectively just removes all formatting.

"""

from abc import ABC, abstractmethod

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
    
    The idea of ten8t markup is a way to tag all result message with formatting information that
    may be used to provide the end user with a richer formatting experience targeting multiple
    output environments.  Since I use rich, markdown and streamlit and a bit of HTML I needed it
    to work for those platforms.  
    
    Ten8t messages can have embedded formatting information that indicates to higher level
    code how the text could be formatted.  Rendering class can choose what to do with the tags
    including doing nothing.
    
    The markup looks like html, with open and close tags.  This was chosen to make the simple
    search/replace algorithm have easy matches.
    
    The idea is that you could want a way to write a red message, so you could do:
    
    "Hello <<red>>world!<<red>>"
    
    or perhaps in code 
    
    f"Hello {fmt.red('world!')}"
    
    to make your formatted output.  
    
    If no formatter was specified, a text formatter would just run through the code and strip out
    all the <<>> tags, leaving the plain text:
    
    Hello world!
    
    A rich formatter might replace those tags with:
    
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

    def __init__(self, open_delim: str = "<<@>>", close_delim: str = "<</@>>"):
        """
        Init only allows you to specify open and close delimiters.
        
        The assumption is that you want markup that looks like <<bold>> <</bold>> and this
        __init__ defaults to those delimiters.  
        
        If you don't like the <<>> then you can change it.
        
        """
        self.open_delim = open_delim
        self.close_delim = close_delim

        if open_delim == close_delim:
            raise ValueError("Open and close delimiters for markup should not be the same.")

    def open_tag(self, tag: str) -> str:
        """if tag is 'red' open tag is <<red>>"""
        odl = self.open_delim.replace("@", tag.strip())
        return odl

    def close_tag(self, tag: str) -> str:
        """If  tag is 'red' close tag is <</red>>"""
        cdl = self.close_delim.replace("@", tag.strip())
        return cdl

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


class Ten8tAbstractRender(ABC):
    """
    Base class for all ten8t renderers.  This has a list of all supported tags, the abstract
    render method and a concrete cleanup that removes all un-rendered tags.
    """

    # List of all known tags.  We need the list of all tags because code will need to run through all
    # tags and remove them if they aren't formatted.
    tags = [TAG_BOLD, TAG_ITALIC, TAG_UNDERLINE, TAG_STRIKETHROUGH, TAG_DATA, TAG_EXPECTED, TAG_ACTUAL, TAG_FAIL,
            TAG_PASS, TAG_CODE, TAG_RED, TAG_BLUE, TAG_GREEN, TAG_PURPLE, TAG_ORANGE, TAG_YELLOW, TAG_BLACK, TAG_WHITE,
            TAG_WARN, TAG_SKIP]

    @abstractmethod
    def render(self, msg):  # pragma: no cover
        """Base class render method"""

    def cleanup(self, msg):
        """
        It is optional for subclasses to replace all the render tags.  This method provides
        support to wipeout all un rendered tags.
        """
        fmt = Ten8tMarkup()

        # Find all the defined tags and blow them away.
        for tag in self.tags:
            msg = msg.replace(f'{fmt.open_tag(tag)}', '').replace(f'{fmt.close_tag(tag)}', '')
        return msg


class Ten8tRenderText(Ten8tAbstractRender):
    """
    This class strips all html formatting and is suitable for text output for things like CLI or API
    
    These messages are generally considered 'one-liners'
    """

    def render(self, msg):
        # Call the baseclass cleanup messages since this is a do-nothing class.
        return self.cleanup(msg)


class Ten8tBasicMarkdown(Ten8tRenderText):
    """Markdown render class"""

    def render(self, msg):
        """Basic markdown render method that converts tags to markdown"""
        fmt = Ten8tMarkup()
        replacements = {TAG_BOLD: '**',
                        TAG_ITALIC: '*',
                        TAG_STRIKETHROUGH: '~~',
                        TAG_CODE: '`',
                        TAG_PASS: '`',
                        TAG_FAIL: '`',
                        TAG_WARN: '`',
                        TAG_SKIP: '`',
                        TAG_EXPECTED: '`',
                        TAG_ACTUAL: '`'}
        # Phase 1 replace all substitutions
        for md, replacement in replacements.items():
            open_tag = fmt.open_tag(md)
            close_tag = fmt.close_tag(md)
            msg = msg.replace(open_tag, replacement).replace(close_tag, replacement)

        # Phase 2 replace all unused tags.
        return self.cleanup(msg)


class Ten8tBasicRichRenderer(Ten8tRenderText):
    """Rich render class"""

    def render(self, msg):
        """Basic markdown render method that converts tags to rich formatted code"""
        fmt = Ten8tMarkup()
        replacements = {TAG_BOLD: ('[bold]', '[/bold]'),
                        TAG_ITALIC: ('[italic]', '[/italic]'),
                        TAG_UNDERLINE: ('[u]', '[/u]'),
                        TAG_STRIKETHROUGH: ('[strike]', '[/strike]'),
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

        # Phase 1 replace all substitutions
        for md, replacement in replacements.items():
            msg = msg.replace(f"{fmt.open_tag(md)}", replacement[0]).replace(f"{fmt.close_tag(md)}", replacement[1])

        # Phase 2 replace all unused tags.
        return self.cleanup(msg)


class Ten8tBasicStreamlitRenderer(Ten8tRenderText):
    """Streamlit renderer class."""

    def render(self, msg):
        """Basic markdown render method that converts tags to streamlit format strings"""

        fmt = Ten8tMarkup()
        replacements = {
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
            TAG_BLACK: (':black[', ']'),
            TAG_WHITE: (':white[', ']'),
        }

        # Phase 1 replace all substitutions
        for md, replacement in replacements.items():
            open_tag = fmt.open_tag(md)
            close_tag = fmt.close_tag(md)

            msg = msg.replace(open_tag, replacement[0]).replace(close_tag, replacement[1])

        # Phase 2 replace all unused tags.
        msg = self.cleanup(msg)

        return msg


class Ten8tBasicHTMLRenderer(Ten8tRenderText):
    """HTML renderer"""

    def render(self, msg):
        """Basic markdown render method that converts tags to html"""

        fmt = Ten8tMarkup()
        replacements = {
            TAG_BOLD: ('<b>', '</b>'),
            TAG_ITALIC: ('<i>', '</i>'),
            TAG_UNDERLINE: ('<u>', '</u>'),
            TAG_STRIKETHROUGH: ('<s>', '</s>'),
            TAG_CODE: ('<code>', '</code>'),
            TAG_PASS: ('<span style="color:green">', '</span>'),
            TAG_FAIL: ('<span style="color:red">', '</span>'),
            TAG_WARN: ('<span style="color:orange">', '</span>'),
            TAG_SKIP: ('<span style="color:purple">', '</span>'),
            TAG_EXPECTED: ('<span style="color:green">', '</span>'),
            TAG_ACTUAL: ('<span style="color:red">', '</span>'),
            TAG_RED: ('<span style="color:red">', '</span>'),
            TAG_GREEN: ('<span style="color:green">', '</span>'),
            TAG_BLUE: ('<span style="color:blue">', '</span>'),
            TAG_YELLOW: ('<span style="color:yellow">', '</span>'),
            TAG_ORANGE: ('<span style="color:orange">', '</span>'),
            TAG_PURPLE: ('<span style="color:purple">', '</span>'),
            TAG_BLACK: ('<span style="color:black">', '</span>'),
            TAG_WHITE: ('<span style="color:white">', '</span>'),
        }

        # Phase 1 replace all substitutions
        for md, replacement in replacements.items():
            open_tag = fmt.open_tag(md)
            close_tag = fmt.close_tag(md)

            msg = msg.replace(open_tag, replacement[0]).replace(close_tag, replacement[1])

        # Phase 2 replace all unused tags.
        msg = self.cleanup(msg)

        return msg
