from .config import Ten8tDumpConfig
from .csv import Ten8tDumpCSV
from .markdown import Ten8tDumpMarkdown
from ..ten8t_checker import Ten8tChecker


# Backward compatibility functions
def ten8t_save_csv(ch: Ten8tChecker, config: Ten8tDumpConfig = None):
    """
    Legacy function for backward compatibility.

    Args:
        ch: Ten8tChecker instance containing results
        config: Configuration object for the dump process (None for default)
        quoting: CSV quoting style (if None, determined by config.quoted_strings)
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
        csv_cols: Columns to include in CSV (None for default)
        csv_file: Output CSV filename (None for stdout)
        quoting: CSV quoting style
    """
    config = config or Ten8tDumpConfig.markdown_default()
    dumper = Ten8tDumpMarkdown(config)
    dumper.dump(ch)

