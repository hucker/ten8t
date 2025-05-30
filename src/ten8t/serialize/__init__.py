""" Import main classes to expose at the serialization package level """
from ten8t.serialize.concrete import Ten8tDumpCSV, Ten8tDumpExcel, Ten8tDumpHTML, Ten8tDumpMarkdown, Ten8tDumpSQLite
from ._base import Ten8tDump
from ._config import Ten8tDumpConfig
# from .excel import Ten8tDumpExcel  # If implemented
from ._legacy import ten8t_save_csv, ten8t_save_html, ten8t_save_md, ten8t_save_sqlite, ten8t_save_xls

# For backwards compatibility
__all__ = [
    'Ten8tDumpConfig',
    'Ten8tDump',
    'Ten8tDumpExcel',
    'Ten8tDumpCSV',
    'Ten8tDumpSQLite',
    'Ten8tDumpMarkdown',
    'Ten8tDumpHTML',
    'ten8t_save_csv',
    'ten8t_save_md',
    'ten8t_save_xls',
    'ten8t_save_html',
    'ten8t_save_sqlite',
]
