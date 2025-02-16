"""
This module makes dealing with configuration files a bit easier as it supports JSON and TOML
out of the box.

I also have begun using the patch statement and this was a reasonable place to use it soe
I have provided two implementations.
"""

import sys

from .ten8t_exception import Ten8tException
from .ten8t_inirc import Ten8tIniRC
from .ten8t_jsonrc import Ten8tJsonRC
from .ten8t_rc import Ten8tRC
from .ten8t_tomlrc import Ten8tTomlRC
from .ten8t_xmlrc import Ten8tXMLRC

if sys.version_info[:2] >= (3, 10):
    def ten8t_rc_factory(param: dict | str, section: str = "") -> Ten8tRC:
        """
        Factory function to create an instance of Ten8tRC or its subclasses for Python 3.10 and above.
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
        Factory function to create an instance of Ten8tRC or its subclasses for Python below 3.10.
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
