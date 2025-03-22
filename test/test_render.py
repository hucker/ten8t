"""
Test the render subpackage.  This package has markup for many different
backends...which is a glorified search and replace engine.
"""

import pytest

from ten8t import render


def test_format_exc():
    with pytest.raises(ValueError):
        _ = render.Ten8tMarkup(open_delim='<@>', close_delim='<@>')


@pytest.mark.parametrize("tag,func,input_,expected_output", [
    (render.TAG_BOLD, render.Ten8tMarkup().bold, "Hello, World!", "<<b>>Hello, World!<</b>>"),
    (render.TAG_ITALIC, render.Ten8tMarkup().italic, "Hello, World!", "<<i>>Hello, World!<</i>>"),
    (render.TAG_UNDERLINE, render.Ten8tMarkup().underline, "Hello, World!", "<<u>>Hello, World!<</u>>"),
    (render.TAG_STRIKETHROUGH, render.Ten8tMarkup().strikethrough, "Hello, World!", "<<s>>Hello, World!<</s>>"),
    (render.TAG_CODE, render.Ten8tMarkup().code, "Hello, World!", "<<code>>Hello, World!<</code>>"),
    (render.TAG_PASS, render.Ten8tMarkup().pass_, "Hello, World!", "<<pass>>Hello, World!<</pass>>"),
    (render.TAG_FAIL, render.Ten8tMarkup().fail, "Hello, World!", "<<fail>>Hello, World!<</fail>>"),
    (render.TAG_SKIP, render.Ten8tMarkup().skip, "Hello, World!", "<<skip>>Hello, World!<</skip>>"),
    (render.TAG_WARN, render.Ten8tMarkup().warn, "Hello, World!", "<<warn>>Hello, World!<</warn>>"),
    (render.TAG_EXPECTED, render.Ten8tMarkup().expected, "Hello, World!", "<<expected>>Hello, World!<</expected>>"),
    (render.TAG_ACTUAL, render.Ten8tMarkup().actual, "Hello, World!", "<<actual>>Hello, World!<</actual>>"),
    (render.TAG_RED, render.Ten8tMarkup().red, "Hello, World!", "<<red>>Hello, World!<</red>>"),
    (render.TAG_BLUE, render.Ten8tMarkup().blue, "Hello, World!", "<<blue>>Hello, World!<</blue>>"),
    (render.TAG_GREEN, render.Ten8tMarkup().green, "Hello, World!", "<<green>>Hello, World!<</green>>"),
    (render.TAG_PURPLE, render.Ten8tMarkup().purple, "Hello, World!", "<<purple>>Hello, World!<</purple>>"),
    (render.TAG_ORANGE, render.Ten8tMarkup().orange, "Hello, World!", "<<orange>>Hello, World!<</orange>>"),
    (render.TAG_YELLOW, render.Ten8tMarkup().yellow, "Hello, World!", "<<yellow>>Hello, World!<</yellow>>"),
    (render.TAG_BLACK, render.Ten8tMarkup().black, "Hello, World!", "<<black>>Hello, World!<</black>>"),
    (render.TAG_WHITE, render.Ten8tMarkup().white, "Hello, World!", "<<white>>Hello, World!<</white>>"),
])
def test_all_tags(tag, func, input_, expected_output):
    assert func(input_) == expected_output


@pytest.mark.parametrize("markup_func,input_,expected_output", [
    (render.Ten8tMarkup().bold, "Hello, World!", "Hello, World!"),
    (render.Ten8tMarkup().italic, "Hello, World!", "Hello, World!"),
    (render.Ten8tMarkup().underline, "Hello, World!", "Hello, World!"),
    (render.Ten8tMarkup().strikethrough, "Hello, World!", "Hello, World!"),
    (render.Ten8tMarkup().code, "Hello, World!", "Hello, World!"),
    (render.Ten8tMarkup().data, "Hello, World!", "Hello, World!"),
    (render.Ten8tMarkup().expected, "Hello, World!", "Hello, World!"),
    (render.Ten8tMarkup().actual, "Hello, World!", "Hello, World!"),
    (render.Ten8tMarkup().fail, "Hello, World!", "Hello, World!"),
    (render.Ten8tMarkup().warn, "Hello, World!", "Hello, World!"),
    (render.Ten8tMarkup().skip, "Hello, World!", "Hello, World!"),
    (render.Ten8tMarkup().pass_, "Hello, World!", "Hello, World!"),
    (render.Ten8tMarkup().red, "Hello, World!", "Hello, World!"),
    (render.Ten8tMarkup().blue, "Hello, World!", "Hello, World!"),
    (render.Ten8tMarkup().green, "Hello, World!", "Hello, World!"),
    (render.Ten8tMarkup().purple, "Hello, World!", "Hello, World!"),
    (render.Ten8tMarkup().orange, "Hello, World!", "Hello, World!"),
    (render.Ten8tMarkup().yellow, "Hello, World!", "Hello, World!"),
    (render.Ten8tMarkup().black, "Hello, World!", "Hello, World!"),
    (render.Ten8tMarkup().white, "Hello, World!", "Hello, World!")
])
def test_ten8t_render_text(markup_func, input_, expected_output):
    render_text = render.Ten8tTextRenderer()
    formatted_input = markup_func(input_)
    assert render_text.render(formatted_input) == expected_output


@pytest.mark.parametrize("markup_func,input_,expected_output", [
    (render.Ten8tMarkup().bold, "Hello, World!", "**Hello, World!**"),
    (render.Ten8tMarkup().italic, "Hello, World!", "*Hello, World!*"),

    (render.Ten8tMarkup().strikethrough, "Hello, World!", "~~Hello, World!~~"),
    (render.Ten8tMarkup().code, "Hello, World!", "`Hello, World!`"),
    (render.Ten8tMarkup().pass_, "Hello, World!", "`Hello, World!`"),
    (render.Ten8tMarkup().fail, "Hello, World!", "`Hello, World!`"),
    (render.Ten8tMarkup().warn, "Hello, World!", "`Hello, World!`"),
    (render.Ten8tMarkup().skip, "Hello, World!", "`Hello, World!`"),
    (render.Ten8tMarkup().expected, "Hello, World!", "`Hello, World!`"),
    (render.Ten8tMarkup().actual, "Hello, World!", "`Hello, World!`"),
    # For color markups in markdown, we assume Ten8tBasicMarkdown 
    # does no formatting, hence the expected output is plain text.
    (render.Ten8tMarkup().red, "Hello, World!", "Hello, World!"),
    (render.Ten8tMarkup().blue, "Hello, World!", "Hello, World!"),
    (render.Ten8tMarkup().green, "Hello, World!", "Hello, World!"),
    (render.Ten8tMarkup().purple, "Hello, World!", "Hello, World!"),
    (render.Ten8tMarkup().orange, "Hello, World!", "Hello, World!"),
    (render.Ten8tMarkup().yellow, "Hello, World!", "Hello, World!"),
    (render.Ten8tMarkup().black, "Hello, World!", "Hello, World!"),
    (render.Ten8tMarkup().white, "Hello, World!", "Hello, World!"),
    (render.Ten8tMarkup().underline, "Hello, World!", "Hello, World!"),
])
def test_ten8t_basic_markdown(markup_func, input_, expected_output):
    markdown_render = render.Ten8tBasicMarkdownRenderer()
    formatted_input = markup_func(input_)
    output = markdown_render.render(formatted_input)
    assert output == expected_output


@pytest.mark.parametrize("markup_func,input_,expected_output", [
    (render.Ten8tMarkup().bold, "Hello, World!", "[bold]Hello, World![/bold]"),
    (render.Ten8tMarkup().italic, "Hello, World!", "[italic]Hello, World![/italic]"),
    (render.Ten8tMarkup().underline, "Hello, World!", "[u]Hello, World![/u]"),
    (render.Ten8tMarkup().strikethrough, "Hello, World!", "[strike]Hello, World![/strike]"),
    (render.Ten8tMarkup().code, "Hello, World!", "Hello, World!"),
    (render.Ten8tMarkup().pass_, "Hello, World!", "[green]Hello, World![/green]"),
    (render.Ten8tMarkup().fail, "Hello, World!", "[red]Hello, World![/red]"),
    (render.Ten8tMarkup().warn, "Hello, World!", "[orange]Hello, World![/orange]"),
    (render.Ten8tMarkup().skip, "Hello, World!", "[purple]Hello, World![/purple]"),
    (render.Ten8tMarkup().expected, "Hello, World!", "[green]Hello, World![/green]"),
    (render.Ten8tMarkup().actual, "Hello, World!", "[green]Hello, World![/green]"),
    (render.Ten8tMarkup().red, "Hello, World!", "[red]Hello, World![/red]"),
    (render.Ten8tMarkup().blue, "Hello, World!", "[blue]Hello, World![/blue]"),
    (render.Ten8tMarkup().green, "Hello, World!", "[green]Hello, World![/green]"),
    (render.Ten8tMarkup().purple, "Hello, World!", "[purple]Hello, World![/purple]"),
    (render.Ten8tMarkup().orange, "Hello, World!", "[orange]Hello, World![/orange]"),
    (render.Ten8tMarkup().yellow, "Hello, World!", "[yellow]Hello, World![/yellow]"),
    (render.Ten8tMarkup().black, "Hello, World!", "[black]Hello, World![/black]"),
    (render.Ten8tMarkup().white, "Hello, World!", "[white]Hello, World![/white]"),
])
def test_ten8t_basic_rich(markup_func, input_, expected_output):
    rich_render = render.Ten8tBasicRichRenderer()
    formatted_input = markup_func(input_)
    output = rich_render.render(formatted_input)
    assert output == expected_output


@pytest.mark.parametrize("markup_func,input_,expected_output", [
    (render.Ten8tMarkup().bold, "Hello, World!", "<b>Hello, World!</b>"),
    (render.Ten8tMarkup().italic, "Hello, World!", "<i>Hello, World!</i>"),
    (render.Ten8tMarkup().underline, "Hello, World!", "<u>Hello, World!</u>"),
    (render.Ten8tMarkup().strikethrough, "Hello, World!", "<s>Hello, World!</s>"),
    (render.Ten8tMarkup().code, "Hello, World!", "<code>Hello, World!</code>"),
    (render.Ten8tMarkup().pass_, "Hello, World!", '<span style="color:green">Hello, World!</span>'),
    (render.Ten8tMarkup().fail, "Hello, World!", '<span style="color:red">Hello, World!</span>'),
    (render.Ten8tMarkup().skip, "Hello, World!", '<span style="color:purple">Hello, World!</span>'),
    (render.Ten8tMarkup().warn, "Hello, World!", '<span style="color:orange">Hello, World!</span>'),
    (render.Ten8tMarkup().expected, "Hello, World!", '<span style="color:green">Hello, World!</span>'),
    (render.Ten8tMarkup().actual, "Hello, World!", '<span style="color:red">Hello, World!</span>'),
    (render.Ten8tMarkup().red, "Hello, World!", '<span style="color:red">Hello, World!</span>'),
    (render.Ten8tMarkup().blue, "Hello, World!", '<span style="color:blue">Hello, World!</span>'),
    (render.Ten8tMarkup().green, "Hello, World!", '<span style="color:green">Hello, World!</span>'),
    (render.Ten8tMarkup().purple, "Hello, World!", '<span style="color:purple">Hello, World!</span>'),
    (render.Ten8tMarkup().orange, "Hello, World!", '<span style="color:orange">Hello, World!</span>'),
    (render.Ten8tMarkup().yellow, "Hello, World!", '<span style="color:yellow">Hello, World!</span>'),
    (render.Ten8tMarkup().black, "Hello, World!", '<span style="color:black">Hello, World!</span>'),
    (render.Ten8tMarkup().white, "Hello, World!", '<span style="color:white">Hello, World!</span>'),
])
def test_ten8t_basic_html_renderer(markup_func, input_, expected_output):
    html_renderer = render.Ten8tBasicHTMLRenderer()
    formatted_input = markup_func(input_)
    output = html_renderer.render(formatted_input)
    assert output == expected_output


@pytest.mark.parametrize("markup_func, input_, expected_output", [
    (render.Ten8tMarkup().bold, "Hello, World!", "**Hello, World!**"),
    (render.Ten8tMarkup().italic, "Hello, World!", "*Hello, World!*"),
    (render.Ten8tMarkup().strikethrough, "Hello, World!", "Hello, World!"),
    (render.Ten8tMarkup().code, "Hello, World!", "`Hello, World!`"),
    (render.Ten8tMarkup().pass_, "Hello, World!", ":green[Hello, World!]"),
    (render.Ten8tMarkup().fail, "Hello, World!", ":red[Hello, World!]"),
    (render.Ten8tMarkup().skip, "Hello, World!", ":purple[Hello, World!]"),
    (render.Ten8tMarkup().warn, "Hello, World!", ":orange[Hello, World!]"),
    (render.Ten8tMarkup().expected, "Hello, World!", ":green[Hello, World!]"),
    (render.Ten8tMarkup().actual, "Hello, World!", ":green[Hello, World!]"),
    (render.Ten8tMarkup().red, "Hello, World!", ":red[Hello, World!]"),
    (render.Ten8tMarkup().green, "Hello, World!", ":green[Hello, World!]"),
    (render.Ten8tMarkup().blue, "Hello, World!", ":blue[Hello, World!]"),
    (render.Ten8tMarkup().yellow, "Hello, World!", ":yellow[Hello, World!]"),
    (render.Ten8tMarkup().orange, "Hello, World!", ":orange[Hello, World!]"),
    (render.Ten8tMarkup().purple, "Hello, World!", ":purple[Hello, World!]"),
    (render.Ten8tMarkup().black, "Hello, World!", ":black[Hello, World!]"),
    (render.Ten8tMarkup().white, "Hello, World!", ":white[Hello, World!]"),

])
def test_ten8t_basic_streamlit_renderer(markup_func, input_, expected_output):
    streamlit_renderer = render.Ten8tBasicStreamlitRenderer()
    formatted_input = markup_func(input_)
    output = streamlit_renderer.render(formatted_input)
    assert output == expected_output


@pytest.mark.parametrize("markup_func", [
    render.Ten8tMarkup().bold,
    render.Ten8tMarkup().italic,
    render.Ten8tMarkup().underline,
    render.Ten8tMarkup().strikethrough,
    render.Ten8tMarkup().code,
    render.Ten8tMarkup().pass_,
    render.Ten8tMarkup().fail,
    render.Ten8tMarkup().expected,
    render.Ten8tMarkup().actual,
    render.Ten8tMarkup().red,
    render.Ten8tMarkup().green,
    render.Ten8tMarkup().blue,
    render.Ten8tMarkup().yellow,
    render.Ten8tMarkup().orange,
    render.Ten8tMarkup().purple,
    render.Ten8tMarkup().black,
    render.Ten8tMarkup().white,
])
def test_ten8t_render_text_with_empty_string(markup_func):
    """All markups with null inputs should map to null outputs."""
    render_text = render.Ten8tTextRenderer()
    input = ""
    expected_output = ""
    formatted_input = markup_func(input)
    output = render_text.render(formatted_input)
    assert output == expected_output
