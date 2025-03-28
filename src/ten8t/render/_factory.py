"""
This module privdes support for creating a singleton object that manages the available renderers.

Because of difficulties in using isinstance to detect inherited classes (because of import naming issues)
this module detects valid renderers using the RendererProtocol.

"""

from typing import Type

from ._base import Ten8tAbstractRenderer
from ._protocol import Ten8tRendererProtocol
from .concrete.github_markdown import Ten8tGitHubMarkdownRenderer
from .concrete.html import Ten8tBasicHTMLRenderer
from .concrete.markdown import Ten8tBasicMarkdownRenderer
from .concrete.rich import Ten8tBasicRichRenderer
from .concrete.streamlit import Ten8tBasicStreamlitRenderer
from .concrete.text import Ten8tTextRenderer
from ..ten8t_exception import Ten8tException, Ten8tValueError


class Ten8tRendererFactory:
    """
    Factory class for creating and managing renderer instances.

    This factory registers and instantiates renderers
    that implement the Ten8tRendererProtocol.
    """

    _instance = None  # Single shared instance


    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls, *args, **kwargs)
        return cls._instance


    def __init__(self):
        if not hasattr(self, "_initialized"):
            self._renderers: dict[str, Type[Ten8tRendererProtocol]] = {}
            self.initialize_renderers()
            self._initialized = True  # Ensure __init__ logic runs only once

    def register_renderer(self, renderer_class: Type[Ten8tAbstractRenderer]) -> None:
        """
        Register a renderer class with the factory.

        Args:
            renderer_class: A class that implements Ten8tRendererProtocol
        """
        if not isinstance(renderer_class, type):
            raise Ten8tValueError(f"Expected a Renderer class, got {type(renderer_class).__name__}")

        # Create a temporary instance to access the name attribute
        instance = renderer_class()
        renderer_name = instance.renderer_name

        self._renderers[renderer_name] = renderer_class

    def discover_renderers(self) -> list[Type[Ten8tAbstractRenderer]]:
        """
        Return a manually defined list of renderer classes.

        Returns:
            A list of renderer classes that implement Ten8tRendererProtocol
        """
        # Return the list of default renderers
        return [
            Ten8tGitHubMarkdownRenderer,
            Ten8tBasicHTMLRenderer,
            Ten8tBasicRichRenderer,
            Ten8tBasicStreamlitRenderer,
            Ten8tTextRenderer,
            Ten8tBasicMarkdownRenderer,
        ]

    def initialize_renderers(self) -> None:
        """
        Initialize the factory with the default renderers.
        This method clears any existing registrations and registers
        the default renderers.
        """
        self._renderers = {}  # Clear existing renderers
        renderer_classes = self.discover_renderers()
        for renderer_class in renderer_classes:
            self.register_renderer(renderer_class)

    def get_renderer(self, name: str) -> Ten8tRendererProtocol:
        """
        Get an instance of the requested renderer.

        Args:
            name: The name of the renderer to instantiate

        Returns:
            An instance of the requested renderer

        Raises:
            ValueError: If no renderer with the given name is registered
        """
        if name not in self._renderers:
            available = ", ".join(self._renderers.keys())
            raise Ten8tValueError(f"Unknown renderer '{name}'. Available renderers: {available}")

        renderer_class = self._renderers[name]
        return renderer_class()

    def get_renderer_for_extension(self, extension: str) -> Ten8tRendererProtocol:
        """
        Find a renderer that supports the given file extension.

        Args:
            extension: The file extension (with or without leading dot)

        Returns:
            An instance of a compatible renderer

        Raises:
            ValueError: If no renderer supports the given extension
        """
        # Ensure extension starts with a dot
        if not extension.startswith('.'):
            extension = f'.{extension}'

        # Find all renderers that support this extension
        compatible_renderers = []
        for name, renderer_class in self._renderers.items():
            # Create instance to check extensions
            instance = renderer_class()
            if extension in instance.file_extensions:
                compatible_renderers.append((name, renderer_class))

        if not compatible_renderers:
            raise Ten8tException(f"No renderer found for extension '{extension}'")

        # If multiple renderers support this extension, use the first one
        name, renderer_class = compatible_renderers[0]
        return renderer_class()

    def list_available_renderers(self) -> list[str]:
        """
        Get a list of all available renderer names.

        Returns:
            A list of renderer names
        """
        return list(self._renderers.keys())

    def get_supported_extensions(self) -> dict[str, list[str]]:
        """
        Get a dictionary of supported file extensions for each renderer.

        Returns:
            A dictionary mapping renderer names to lists of supported extensions
        """
        extensions = {}
        for name, renderer_class in self._renderers.items():
            instance = renderer_class()
            extensions[name] = instance.file_extensions.copy()
        return extensions
