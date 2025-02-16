"""
These the rc factory method allowing fairly easily to have various flavors or RC files to
be interchangeable.

"""

import pytest

from ten8t import Ten8tMarkup
from ten8t import ten8t_format


def test_format_exc():
    with pytest.raises(ValueError):
        _ = Ten8tMarkup(open_delim='<@>', close_delim='<@>')


@pytest.mark.parametrize("tag,func,input,expected_output", [
    (ten8t_format.TAG_BOLD, Ten8tMarkup().bold, "Hello, World!", "<<b>>Hello, World!<</b>>"),
    (ten8t_format.TAG_ITALIC, Ten8tMarkup().italic, "Hello, World!", "<<i>>Hello, World!<</i>>"),
    (ten8t_format.TAG_UNDERLINE, Ten8tMarkup().underline, "Hello, World!", "<<u>>Hello, World!<</u>>"),
    (ten8t_format.TAG_STRIKETHROUGH, Ten8tMarkup().strikethrough, "Hello, World!", "<<s>>Hello, World!<</s>>"),
    (ten8t_format.TAG_CODE, Ten8tMarkup().code, "Hello, World!", "<<code>>Hello, World!<</code>>"),
    (ten8t_format.TAG_PASS, Ten8tMarkup().pass_, "Hello, World!", "<<pass>>Hello, World!<</pass>>"),
    (ten8t_format.TAG_FAIL, Ten8tMarkup().fail, "Hello, World!", "<<fail>>Hello, World!<</fail>>"),
    (ten8t_format.TAG_SKIP, Ten8tMarkup().skip, "Hello, World!", "<<skip>>Hello, World!<</skip>>"),
    (ten8t_format.TAG_WARN, Ten8tMarkup().warn, "Hello, World!", "<<warn>>Hello, World!<</warn>>"),
    (ten8t_format.TAG_EXPECTED, Ten8tMarkup().expected, "Hello, World!", "<<expected>>Hello, World!<</expected>>"),
    (ten8t_format.TAG_ACTUAL, Ten8tMarkup().actual, "Hello, World!", "<<actual>>Hello, World!<</actual>>"),
    (ten8t_format.TAG_RED, Ten8tMarkup().red, "Hello, World!", "<<red>>Hello, World!<</red>>"),
    (ten8t_format.TAG_BLUE, Ten8tMarkup().blue, "Hello, World!", "<<blue>>Hello, World!<</blue>>"),
    (ten8t_format.TAG_GREEN, Ten8tMarkup().green, "Hello, World!", "<<green>>Hello, World!<</green>>"),
    (ten8t_format.TAG_PURPLE, Ten8tMarkup().purple, "Hello, World!", "<<purple>>Hello, World!<</purple>>"),
    (ten8t_format.TAG_ORANGE, Ten8tMarkup().orange, "Hello, World!", "<<orange>>Hello, World!<</orange>>"),
    (ten8t_format.TAG_YELLOW, Ten8tMarkup().yellow, "Hello, World!", "<<yellow>>Hello, World!<</yellow>>"),
    (ten8t_format.TAG_BLACK, Ten8tMarkup().black, "Hello, World!", "<<black>>Hello, World!<</black>>"),
    (ten8t_format.TAG_WHITE, Ten8tMarkup().white, "Hello, World!", "<<white>>Hello, World!<</white>>"),
])
def test_all_tags(tag, func, input, expected_output):
    assert func(input) == expected_output


@pytest.mark.parametrize("markup_func,input,expected_output", [
    (Ten8tMarkup().bold, "Hello, World!", "Hello, World!"),
    (Ten8tMarkup().italic, "Hello, World!", "Hello, World!"),
    (Ten8tMarkup().underline, "Hello, World!", "Hello, World!"),
    (Ten8tMarkup().strikethrough, "Hello, World!", "Hello, World!"),
    (Ten8tMarkup().code, "Hello, World!", "Hello, World!"),
    (Ten8tMarkup().data, "Hello, World!", "Hello, World!"),
    (Ten8tMarkup().expected, "Hello, World!", "Hello, World!"),
    (Ten8tMarkup().actual, "Hello, World!", "Hello, World!"),
    (Ten8tMarkup().fail, "Hello, World!", "Hello, World!"),
    (Ten8tMarkup().warn, "Hello, World!", "Hello, World!"),
    (Ten8tMarkup().skip, "Hello, World!", "Hello, World!"),
    (Ten8tMarkup().pass_, "Hello, World!", "Hello, World!"),
    (Ten8tMarkup().red, "Hello, World!", "Hello, World!"),
    (Ten8tMarkup().blue, "Hello, World!", "Hello, World!"),
    (Ten8tMarkup().green, "Hello, World!", "Hello, World!"),
    (Ten8tMarkup().purple, "Hello, World!", "Hello, World!"),
    (Ten8tMarkup().orange, "Hello, World!", "Hello, World!"),
    (Ten8tMarkup().yellow, "Hello, World!", "Hello, World!"),
    (Ten8tMarkup().black, "Hello, World!", "Hello, World!"),
    (Ten8tMarkup().white, "Hello, World!", "Hello, World!")
])
def test_ten8t_render_text(markup_func, input, expected_output):
    render_text = ten8t_format.Ten8tRenderText()
    formatted_input = markup_func(input)
    assert render_text.render(formatted_input) == expected_output


@pytest.mark.parametrize("markup_func,input,expected_output", [
    (Ten8tMarkup().bold, "Hello, World!", "**Hello, World!**"),
    (Ten8tMarkup().italic, "Hello, World!", "*Hello, World!*"),

    (Ten8tMarkup().strikethrough, "Hello, World!", "~~Hello, World!~~"),
    (Ten8tMarkup().code, "Hello, World!", "`Hello, World!`"),
    (Ten8tMarkup().pass_, "Hello, World!", "`Hello, World!`"),
    (Ten8tMarkup().fail, "Hello, World!", "`Hello, World!`"),
    (Ten8tMarkup().warn, "Hello, World!", "`Hello, World!`"),
    (Ten8tMarkup().skip, "Hello, World!", "`Hello, World!`"),
    (Ten8tMarkup().expected, "Hello, World!", "`Hello, World!`"),
    (Ten8tMarkup().actual, "Hello, World!", "`Hello, World!`"),
    # For color markups in markdown, we assume Ten8tBasicMarkdown 
    # does no formatting, hence the expected output is plain text.
    (Ten8tMarkup().red, "Hello, World!", "Hello, World!"),
    (Ten8tMarkup().blue, "Hello, World!", "Hello, World!"),
    (Ten8tMarkup().green, "Hello, World!", "Hello, World!"),
    (Ten8tMarkup().purple, "Hello, World!", "Hello, World!"),
    (Ten8tMarkup().orange, "Hello, World!", "Hello, World!"),
    (Ten8tMarkup().yellow, "Hello, World!", "Hello, World!"),
    (Ten8tMarkup().black, "Hello, World!", "Hello, World!"),
    (Ten8tMarkup().white, "Hello, World!", "Hello, World!"),
    (Ten8tMarkup().underline, "Hello, World!", "Hello, World!"),
])
def test_ten8t_basic_markdown(markup_func, input, expected_output):
    markdown_render = ten8t_format.Ten8tBasicMarkdown()
    formatted_input = markup_func(input)
    output = markdown_render.render(formatted_input)
    assert output == expected_output


@pytest.mark.parametrize("markup_func,input,expected_output", [
    (Ten8tMarkup().bold, "Hello, World!", "[bold]Hello, World![/bold]"),
    (Ten8tMarkup().italic, "Hello, World!", "[italic]Hello, World![/italic]"),
    (Ten8tMarkup().underline, "Hello, World!", "[u]Hello, World![/u]"),
    (Ten8tMarkup().strikethrough, "Hello, World!", "[strike]Hello, World![/strike]"),
    (Ten8tMarkup().code, "Hello, World!", "Hello, World!"),
    (Ten8tMarkup().pass_, "Hello, World!", "[green]Hello, World![/green]"),
    (Ten8tMarkup().fail, "Hello, World!", "[red]Hello, World![/red]"),
    (Ten8tMarkup().warn, "Hello, World!", "[orange]Hello, World![/orange]"),
    (Ten8tMarkup().skip, "Hello, World!", "[purple]Hello, World![/purple]"),
    (Ten8tMarkup().expected, "Hello, World!", "[green]Hello, World![/green]"),
    (Ten8tMarkup().actual, "Hello, World!", "[green]Hello, World![/green]"),
    (Ten8tMarkup().red, "Hello, World!", "[red]Hello, World![/red]"),
    (Ten8tMarkup().blue, "Hello, World!", "[blue]Hello, World![/blue]"),
    (Ten8tMarkup().green, "Hello, World!", "[green]Hello, World![/green]"),
    (Ten8tMarkup().purple, "Hello, World!", "[purple]Hello, World![/purple]"),
    (Ten8tMarkup().orange, "Hello, World!", "[orange]Hello, World![/orange]"),
    (Ten8tMarkup().yellow, "Hello, World!", "[yellow]Hello, World![/yellow]"),
    (Ten8tMarkup().black, "Hello, World!", "[black]Hello, World![/black]"),
    (Ten8tMarkup().white, "Hello, World!", "[white]Hello, World![/white]"),
])
def test_ten8t_basic_rich(markup_func, input, expected_output):
    rich_render = ten8t_format.Ten8tBasicRichRenderer()
    formatted_input = markup_func(input)
    output = rich_render.render(formatted_input)
    assert output == expected_output


@pytest.mark.parametrize("markup_func,input,expected_output", [
    (Ten8tMarkup().bold, "Hello, World!", "<b>Hello, World!</b>"),
    (Ten8tMarkup().italic, "Hello, World!", "<i>Hello, World!</i>"),
    (Ten8tMarkup().underline, "Hello, World!", "<u>Hello, World!</u>"),
    (Ten8tMarkup().strikethrough, "Hello, World!", "<s>Hello, World!</s>"),
    (Ten8tMarkup().code, "Hello, World!", "<code>Hello, World!</code>"),
    (Ten8tMarkup().pass_, "Hello, World!", '<span style="color:green">Hello, World!</span>'),
    (Ten8tMarkup().fail, "Hello, World!", '<span style="color:red">Hello, World!</span>'),
    (Ten8tMarkup().skip, "Hello, World!", '<span style="color:purple">Hello, World!</span>'),
    (Ten8tMarkup().warn, "Hello, World!", '<span style="color:orange">Hello, World!</span>'),
    (Ten8tMarkup().expected, "Hello, World!", '<span style="color:green">Hello, World!</span>'),
    (Ten8tMarkup().actual, "Hello, World!", '<span style="color:red">Hello, World!</span>'),
    (Ten8tMarkup().red, "Hello, World!", '<span style="color:red">Hello, World!</span>'),
    (Ten8tMarkup().blue, "Hello, World!", '<span style="color:blue">Hello, World!</span>'),
    (Ten8tMarkup().green, "Hello, World!", '<span style="color:green">Hello, World!</span>'),
    (Ten8tMarkup().purple, "Hello, World!", '<span style="color:purple">Hello, World!</span>'),
    (Ten8tMarkup().orange, "Hello, World!", '<span style="color:orange">Hello, World!</span>'),
    (Ten8tMarkup().yellow, "Hello, World!", '<span style="color:yellow">Hello, World!</span>'),
    (Ten8tMarkup().black, "Hello, World!", '<span style="color:black">Hello, World!</span>'),
    (Ten8tMarkup().white, "Hello, World!", '<span style="color:white">Hello, World!</span>'),
])
def test_ten8t_basic_html_renderer(markup_func, input, expected_output):
    html_renderer = ten8t_format.Ten8tBasicHTMLRenderer()
    formatted_input = markup_func(input)
    output = html_renderer.render(formatted_input)
    assert output == expected_output


@pytest.mark.parametrize("markup_func, input, expected_output", [
    (Ten8tMarkup().bold, "Hello, World!", "**Hello, World!**"),
    (Ten8tMarkup().italic, "Hello, World!", "*Hello, World!*"),
    (Ten8tMarkup().strikethrough, "Hello, World!", "Hello, World!"),
    (Ten8tMarkup().code, "Hello, World!", "`Hello, World!`"),
    (Ten8tMarkup().pass_, "Hello, World!", ":green[Hello, World!]"),
    (Ten8tMarkup().fail, "Hello, World!", ":red[Hello, World!]"),
    (Ten8tMarkup().skip, "Hello, World!", ":purple[Hello, World!]"),
    (Ten8tMarkup().warn, "Hello, World!", ":orange[Hello, World!]"),
    (Ten8tMarkup().expected, "Hello, World!", ":green[Hello, World!]"),
    (Ten8tMarkup().actual, "Hello, World!", ":green[Hello, World!]"),
    (Ten8tMarkup().red, "Hello, World!", ":red[Hello, World!]"),
    (Ten8tMarkup().green, "Hello, World!", ":green[Hello, World!]"),
    (Ten8tMarkup().blue, "Hello, World!", ":blue[Hello, World!]"),
    (Ten8tMarkup().yellow, "Hello, World!", ":yellow[Hello, World!]"),
    (Ten8tMarkup().orange, "Hello, World!", ":orange[Hello, World!]"),
    (Ten8tMarkup().purple, "Hello, World!", ":purple[Hello, World!]"),
    (Ten8tMarkup().black, "Hello, World!", ":black[Hello, World!]"),
    (Ten8tMarkup().white, "Hello, World!", ":white[Hello, World!]"),

])
def test_ten8t_basic_streamlit_renderer(markup_func, input, expected_output):
    streamlit_renderer = ten8t_format.Ten8tBasicStreamlitRenderer()
    formatted_input = markup_func(input)
    output = streamlit_renderer.render(formatted_input)
    assert output == expected_output


@pytest.mark.parametrize("markup_func", [
    Ten8tMarkup().bold,
    Ten8tMarkup().italic,
    Ten8tMarkup().underline,
    Ten8tMarkup().strikethrough,
    Ten8tMarkup().code,
    Ten8tMarkup().pass_,
    Ten8tMarkup().fail,
    Ten8tMarkup().expected,
    Ten8tMarkup().actual,
    Ten8tMarkup().red,
    Ten8tMarkup().green,
    Ten8tMarkup().blue,
    Ten8tMarkup().yellow,
    Ten8tMarkup().orange,
    Ten8tMarkup().purple,
    Ten8tMarkup().black,
    Ten8tMarkup().white,
])
def test_ten8t_render_text_with_empty_string(markup_func):
    """All markups with null inputs should map to null outputs."""
    render_text = ten8t_format.Ten8tRenderText()
    input = ""
    expected_output = ""
    formatted_input = markup_func(input)
    output = render_text.render(formatted_input)
    assert output == expected_output
