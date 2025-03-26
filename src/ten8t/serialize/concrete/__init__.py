"""
Built-in scoring strategies.
"""
from .csv import Ten8tDumpCSV
from .excel import Ten8tDumpExcel
from .markdown import Ten8tDumpMarkdown

__all__ = [
    'Ten8tDumpCSV',
    'Ten8tDumpExcel',
    'Ten8tDumpMarkdown',
]
