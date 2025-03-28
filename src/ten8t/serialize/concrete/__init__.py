"""
Built-in scoring strategies.
"""
from ._csv import Ten8tDumpCSV
from ._excel import Ten8tDumpExcel
from ._markdown import Ten8tDumpMarkdown

__all__ = [
    'Ten8tDumpCSV',
    'Ten8tDumpExcel',
    'Ten8tDumpMarkdown',
]
