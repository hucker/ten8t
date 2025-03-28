"""
All render objects must match this protocol.

NOTE: Test case for using protocols instead of inheritance.
"""
from typing import Protocol, runtime_checkable


@runtime_checkable
class Ten8tRendererProtocol(Protocol):
    """
    Protocol defining what a renderer should implement.

    Any class that implements this protocol must provide:
    - renderer_name: A string identifier for the renderer
    - file_extensions: A list of supported file extensions
    - default_extension: The default file extension for saved output
    - render: A method that transforms input text into rendered output
    - cleanup: A method that performs any necessary cleanup after rendering

    USE CASE:
    If you need a new rendering engine it will need there properties and methods.
    If it doesn't have them registration will fail.  Since you should decrive from
    Ten8tAbstractRenderer you should be fine.  Setting this up as a protocol allows
    for more reliable checks for compatibility than using class inheritance.

    """
    # Required attributes
    renderer_name: str
    file_extensions: list[str]
    default_extension: str

    def render(self, text: str) -> str:
        """
        Render the provided text according to the renderer's format.

        Args:
            text: The input text to render

        Returns:
            The rendered text in the appropriate format
        """


    def cleanup(self) -> None:
        """
        Perform any necessary cleanup operations after rendering.

        This might include closing file handles, releasing resources,
        or resetting internal state.
        """

