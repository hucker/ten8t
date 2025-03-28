"""
Allow the usage of an XML file as an RC file.
"""
import pathlib
from xml.etree import ElementTree

from .._base import Ten8tRC
from ...ten8t_exception import Ten8tException


class Ten8tXMLRC(Ten8tRC):
    """
    Loads configurations from XML files. Extends Ten8tRC.

    This class currently supports only simple XML files for basic use cases.
    If your XML is complex, consider a different solution.
    """

    def __init__(self, cfg: str, section: str):
        """
        Initialize the Ten8tXMLRC instance by loading the XML configuration.

        Args:
            cfg (str): The path to the XML configuration file.
            section (str): The top-level XML tag corresponding to the desired configuration section.
        """
        super().__init__()
        package_data = self._load_config(cfg, section)
        # Convert the attributes in the configuration into inclusion/exclusion lists.
        self.expand_attributes(package_data)

    def _load_config(self, cfg: str, section: str) -> dict:
        """
        Loads configuration data from an XML file for a given section.

        Args:
            cfg (str): The path to the XML configuration file.
            section (str): The top-level XML tag to extract the configuration section.

        Returns:
            dict: A dictionary mapping tags to a list of their respective text elements.

        Raises:
            Ten8tException: If the file does not exist, is invalid XML, or contains unexpected attributes.
        """
        cfg_file = pathlib.Path(cfg)
        try:
            tree = ElementTree.parse(cfg_file)
            root = tree.getroot()
            package_data = {}

            # Iterate through the specified section and retrieve child element data.
            for pkg in root.iter(section):
                for child in pkg:
                    # Collect text from all sub-elements into lists.
                    package_data[child.tag] = [
                        elem.text for elem in child.iter() if elem.text and elem.text.strip()
                    ]

        except (FileNotFoundError, ElementTree.ParseError, AttributeError) as error:
            raise Ten8tException(f"Error in XML config file '{cfg}': {error}") from error

        return package_data
