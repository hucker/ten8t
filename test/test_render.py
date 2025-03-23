"""
Test the render subpackage.  This package has markup for many different
backends...which is a glorified search and replace engine.
"""

from typing import List

import pytest

from ten8t import render


@pytest.fixture
def mock_renderer() -> render.Ten8tRendererProtocol:
    """
    A pytest fixture that returns a mock implementation of RenderProtocol to allow
    testing of registring and running new renderers.
    """

    class MockRenderer(render.Ten8tRendererProtocol):
        @property
        def renderer_name(self) -> str:
            return "mock"

        @property
        def file_extensions(self) -> List[str]:
            return [".mock"]

        def render(self, text: str) -> str:
            return f"mock: {text}"

        def cleanup(self) -> None:
            pass

    # Return  the mock CLASS not instance
    return MockRenderer





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
    render_text = render.Ten8tBasicTextRenderer()
    formatted_input = markup_func(input_)
    assert render_text.render(formatted_input) == expected_output


@pytest.mark.parametrize("markup_func,input_,expected_output", [
    (render.Ten8tMarkup().underline, "Hello, World!", "<u>Hello, World!</u>"),
    (render.Ten8tMarkup().pass_, "Hello, World!", "`Hello, World!`"),
    (render.Ten8tMarkup().bold, "Hello, World!", "**Hello, World!**"),
    (render.Ten8tMarkup().italic, "Hello, World!", "*Hello, World!*"),

    (render.Ten8tMarkup().strikethrough, "Hello, World!", "~~Hello, World!~~"),
    (render.Ten8tMarkup().code, "Hello, World!", "`Hello, World!`"),
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
])
def test_ten8t_basic_markdown(markup_func, input_, expected_output):
    markdown_render = render.Ten8TBasicBasicMarkdownRenderer()
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
    rich_render = render.Ten8TBasicBasicRichRenderer()
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
    html_renderer = render.Ten8TBasicBasicHTMLRenderer()
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
    (render.Ten8tMarkup().black, "Hello, World!", "Hello, World!"),
    (render.Ten8tMarkup().white, "Hello, World!", ":white[Hello, World!]"),

])
def test_ten8t_basic_streamlit_renderer(markup_func, input_, expected_output):
    streamlit_renderer = render.Ten8TBasicBasicStreamlitRenderer()
    formatted_input = markup_func(input_)
    output = streamlit_renderer.render(formatted_input)
    assert output == expected_output



@pytest.mark.parametrize("markup_func,input_,expected_output", [
    (render.Ten8tMarkup().bold, "Hello, World!", "**Hello, World!**"),
    (render.Ten8tMarkup().italic, "Hello, World!", "*Hello, World!*"),
    (render.Ten8tMarkup().underline, "Hello, World!", "<u>Hello, World!</u>"),
    (render.Ten8tMarkup().strikethrough, "Hello, World!", "~~Hello, World!~~"),
    (render.Ten8tMarkup().code, "Hello, World!", "<code>Hello, World!</code>"),
    (render.Ten8tMarkup().pass_, "Hello, World!", '<span style="color:green; font-weight:bold">Hello, World!</span>'),
    (render.Ten8tMarkup().fail, "Hello, World!", '<span style="color:red; font-weight:bold">Hello, World!</span>'),
    (render.Ten8tMarkup().skip, "Hello, World!", '<span style="color:blue; font-weight:bold">Hello, World!</span>'),
    (render.Ten8tMarkup().warn, "Hello, World!", '<span style="color:orange; font-weight:bold">Hello, World!</span>'),
    (render.Ten8tMarkup().expected, "Hello, World!", '<span style="color:green">Expected: Hello, World!</span>'),
    (render.Ten8tMarkup().actual, "Hello, World!", '<span style="color:green">Actual: Hello, World!</span>'),
    (render.Ten8tMarkup().red, "Hello, World!", '<span style="color:red">Hello, World!</span>'),
    (render.Ten8tMarkup().blue, "Hello, World!", '<span style="color:blue">Hello, World!</span>'),
    (render.Ten8tMarkup().green, "Hello, World!", '<span style="color:green">Hello, World!</span>'),
    (render.Ten8tMarkup().purple, "Hello, World!", '<span style="color:purple">Hello, World!</span>'),
    (render.Ten8tMarkup().orange, "Hello, World!", '<span style="color:orange">Hello, World!</span>'),
    (render.Ten8tMarkup().yellow, "Hello, World!", '<span style="color:yellow">Hello, World!</span>'),
    (render.Ten8tMarkup().black, "Hello, World!", '<span style="color:black">Hello, World!</span>'),
    (render.Ten8tMarkup().white, "Hello, World!", '<span style="color:white">Hello, World!</span>'),
    (render.Ten8tMarkup().data, "Hello, World!", "<code>Hello, World!</code>"),
])
def test_github_markdown_renderer(markup_func, input_, expected_output):
    """Test that the GitHub Markdown renderer correctly formats tagged text."""
    github_renderer = render.Ten8tGitHubMarkdownRenderer()
    formatted_input = markup_func(input_)
    output = github_renderer.render(formatted_input)
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
    render_text = render.Ten8tBasicTextRenderer()
    input = ""
    expected_output = ""
    formatted_input = markup_func(input)
    output = render_text.render(formatted_input)
    assert output == expected_output



@pytest.mark.parametrize("renderer_class, expected_name, expected_extensions, expected_default", [
    (render.Ten8tGitHubMarkdownRenderer, "github_markdown", [".md", ".markdown", ".gfm"], ".gfm"),
    (render.Ten8tBasicTextRenderer, "text", [".txt"], ".txt"),
    (render.Ten8TBasicBasicRichRenderer, "rich", [], ""),
    (render.Ten8TBasicBasicMarkdownRenderer, "basic_markdown", [".md", ".markdown"], ".md"),
    (render.Ten8TBasicBasicStreamlitRenderer, "streamlit", [], ""),
    (render.Ten8TBasicBasicHTMLRenderer, "basic_html", [".html", ".htm"], ".html"),
])
def test_renderer_attributes(renderer_class, expected_name, expected_extensions, expected_default):
    renderer = renderer_class()
    assert renderer.renderer_name == expected_name
    assert set(renderer.file_extensions) == set(expected_extensions)
    assert renderer.default_extension == expected_default




def test_singleton_behavior(mock_renderer):
    """Test that the factory always returns the same singleton instance and shares state."""
    # Create two references to the factory
    factory1 = render.Ten8tRendererFactory()
    factory2 = render.Ten8tRendererFactory()

    # Confirm both references point to the same instance
    assert factory1 is factory2
    assert id(factory1) == id(factory2)

    # Modify the state of the first reference
    factory1.register_renderer(mock_renderer)

    # Verify the state is reflected in the 'second' reference
    assert "mock" in factory2.list_available_renderers(), (
        "State was not shared between singleton references"
    )


def test_register_renderer_singleton_behavior(mock_renderer):
    """
    Test registering a custom renderer when using the singleton factory
    and verify all access points reflect the change.
    """
    factory1 = render.Ten8tRendererFactory()
    factory1.register_renderer(mock_renderer)

    # Access the same factory instance from another reference
    factory2 = render.Ten8tRendererFactory()
    assert "mock" in factory2.list_available_renderers()

    # Verify renderer instance works
    renderer = factory2.get_renderer("mock")
    assert renderer.renderer_name == "mock"
    assert renderer.render("example") == "mock: example"


def test_list_available_renderers():
    """Test listing all renderers available in the factory."""
    factory = render.Ten8tRendererFactory()
    renderers = factory.list_available_renderers()

    # Check that essential renderers (e.g., markdown, html, text) exist
    assert "basic_markdown" in renderers
    assert "basic_html" in renderers
    assert "text" in renderers


def test_get_renderer():
    """Test retrieving a renderer by its name."""
    factory = render.Ten8tRendererFactory()

    markdown_renderer = factory.get_renderer("basic_markdown")
    assert markdown_renderer.renderer_name == "basic_markdown"

    # Invalid renderer name should raise a ValueError
    with pytest.raises(Exception) as excinfo:
        factory.get_renderer("nonexistent")
    assert "Unknown renderer 'nonexistent'" in str(excinfo.value)


def test_get_renderer_for_extension():
    """Test retrieving a renderer for a given file extension."""
    factory = render.Ten8tRendererFactory()

    # Known extension
    markdown_renderer = factory.get_renderer_for_extension(".md")
    assert markdown_renderer.renderer_name in ["markdown", "github_markdown"]

    # Without dot
    html_renderer = factory.get_renderer_for_extension("html")
    assert html_renderer.renderer_name == "basic_html"

    # Invalid extension
    with pytest.raises(Exception) as excinfo:
        factory.get_renderer_for_extension(".unknown")
    assert "No renderer found for extension '.unknown'" in str(excinfo.value)


def test_get_supported_extensions():
    """Test retrieving all supported file extensions for available renderers."""
    factory = render.Ten8tRendererFactory()

    extensions = factory.get_supported_extensions()

    # Verify the expected extensions
    assert "basic_markdown" in extensions
    assert ".md" in extensions["basic_markdown"]

    assert "basic_html" in extensions
    assert ".html" in extensions["basic_html"]

    assert "text" in extensions
    assert ".txt" in extensions["text"]


def test_custom_renderer_cleanup(mock_renderer):
    """
    Test adding a custom renderer to the singleton factory and confirm
    the shared instance reflects the new functionality.
    """


    # Register custom renderer
    factory = render.Ten8tRendererFactory()
    factory.register_renderer(mock_renderer)

    # Verify its presence
    assert "mock" in factory.list_available_renderers()

    # Re-initialize renderers (should remove custom ones)
    factory.initialize_renderers()
    assert "mock" not in factory.list_available_renderers()
