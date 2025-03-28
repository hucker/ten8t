"""
This module makes dealing with configuration files a bit easier as it supports JSON and TOML
out of the box.

I also have begun using the patch statement and this was a reasonable place to use it soe
I have provided two implementations.
"""

import sys

from ._base import Ten8tRC
from .concrete._ini import Ten8tIniRC
from .concrete._json import Ten8tJsonRC
from .concrete._toml import Ten8tTomlRC
from .concrete._xml import Ten8tXMLRC
from ..ten8t_exception import Ten8tException

if sys.version_info[:2] >= (3, 10):
    def ten8t_rc_factory(param: dict | str, section: str = "") -> Ten8tRC:
        """
        Creates an instance of a resource configuration class (Ten8tRC) based on the type of
        the input parameter. The parameter can be a dictionary or a string representing a path
        to a supported configuration file (.toml, .json, .xml, .ini). If the section argument
        is provided, it directs the factory to return a specific section of the configuration
        data. The factory facilitates configuration resource management depending on input type.

        Args:
            param (dict | str): A dictionary representing the resource configuration directly,
                or a string that specifies the path to a configuration file. Supported
                file extensions are '.toml', '.json', '.xml', and '.ini'.
            section (str, optional): Specifies a configuration section to extract. If not
                provided and when 'param' is a dictionary, the entire dictionary will be
                used. Defaults to an empty string.

        Raises:
            Ten8tException: If the provided parameter type is invalid or if the file type in
                the string parameter is unsupported.

        Returns:
            Ten8tRC: An instance of the Ten8tRC class (or derived class) containing the
                configuration based on the input parameter.
        """
        match param:
            case dict(d):
                if section == "":
                    return Ten8tRC(rc_d=d)
                else:
                    return Ten8tRC(rc_d=d[section])
            case str(s) if s.endswith('.toml'):
                return Ten8tTomlRC(cfg=s, section=section)
            case str(s) if s.endswith('.json'):
                return Ten8tJsonRC(cfg=s, section=section)
            case str(s) if s.endswith('.xml'):
                return Ten8tXMLRC(cfg=s, section=section)
            case str(s) if s.endswith('.ini'):
                return Ten8tIniRC(cfg=s, section=section)
            case _:
                raise Ten8tException('Invalid parameter type for ten8t_rc_factory.')
else:  # pragma: no cover
    def ten8t_rc_factory(param, section: str = "") -> Ten8tRC:
        """
        Factory function to create a configuration object based on the input type and format. This
        function processes the input parameter and generates the appropriate Ten8tRC object instance
        by interpreting the parameter type and corresponding section.

        Args:
            param: The parameter used to create the configuration object. It can be a dictionary
                or a string representing a file path. Supported file formats include `.toml`,
                `.json`, `.xml`, and `.ini`.
            section (str): The specific section to extract from the configuration when applicable.
                This is used when the input parameter is either a file path or a dictionary
                representing a configuration with multiple sections.

        Returns:
            Ten8tRC: The configuration object generated based on the input parameter and its
            type or specified section.

        Raises:
            Ten8tException: If the input parameter type is invalid or if the provided string does
            not represent a supported configuration file format.
        """
        if isinstance(param, dict):
            if not section:
                return Ten8tRC(rc_d=param)
            else:
                return Ten8tRC(rc_d=param[section])
        elif isinstance(param, str):
            if param.endswith('.toml'):
                return Ten8tTomlRC(cfg=param, section=section)
            elif param.endswith('.json'):
                return Ten8tJsonRC(cfg=param, section=section)
            elif param.endswith('.xml'):
                return Ten8tXMLRC(cfg=param, section=section)
            elif param.endswith('.ini'):
                return Ten8tIniRC(cfg=param, section=section)

        raise Ten8tException(f'Invalid parameter type for ten8t_rc_factory {param=}-{section=}.')
