# Import main classes to expose at the serialization package level
from .base import Ten8tDump
from .config import Ten8tDumpConfig
from .csv import Ten8tDumpCSV
# from .excel import Ten8tDumpExcel  # If implemented
from .legacy import ten8t_save_csv, ten8t_save_md
from .markdown import Ten8tDumpMarkdown

# For backwards compatibility
__all__ = [
    'Ten8tDumpConfig',
    'Ten8tDump',
    'Ten8tDumpCSV',
    'Ten8tDumpMarkdown',
#    'Ten8tDumpExcel',  # If implemented
    'ten8t_save_csv',
    'ten8t_save_md'
]
