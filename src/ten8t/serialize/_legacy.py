"""
The functions in this module used to be hand coded, they not use the serialazation classes.
"""

from ._config import Ten8tDumpConfig
from .concrete._csv import Ten8tDumpCSV
from .concrete._excel import Ten8tDumpExcel
from .concrete._markdown import Ten8tDumpMarkdown
from ..ten8t_checker import Ten8tChecker


# Backward compatibility functions
def ten8t_save_csv(ch: Ten8tChecker, config: Ten8tDumpConfig = None):
    """
    Legacy function for backward compatibility.

    Args:
        ch: Ten8tChecker instance containing results
        config: Configuration object for the dump process (None for default)
    """
    # Use default config if none provided
    config = config or Ten8tDumpConfig.csv_default()

    # Create CSV dumper with config
    dumper = Ten8tDumpCSV(config)

    # Dump to the output file specified in config
    dumper.dump(ch)


def ten8t_save_md(ch: Ten8tChecker,
                  config:Ten8tDumpConfig=None):
    """
    Legacy function for backward compatibility.

    Args:
        ch: Ten8tChecker instance containing results
        config: Configuration object for the dump process (None for default)
    """
    config = config or Ten8tDumpConfig.markdown_default()
    dumper = Ten8tDumpMarkdown(config)
    dumper.dump(ch)


def ten8t_save_xls(ch: Ten8tChecker,
                   config: Ten8tDumpConfig = None):
    """
    Legacy function for backward compatibility.

    Args:
        ch: Ten8tChecker instance containing results
        config: Configuration object for the dump process (None for default)
    """
    config = config or Ten8tDumpConfig.excel_default()
    dumper = Ten8tDumpExcel(config)
    dumper.dump(ch)
