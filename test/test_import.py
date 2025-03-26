"""Versioning tests """
import re

from src import ten8t as t8


# @pytest.mark.run(order=-1)
def test_import_packages():
    """Crude test to verify that the built in rules are imported by default"""
    installstring=t8.whats_installed()
       
    assert installstring == 'fs,narwhals,openpyxl,pathlib,pdf,ping,requests,sqlalchemy'

    assert t8.is_installed('fs')
    assert t8.is_installed('narwhals')
    assert t8.is_installed('openpyxl')
    assert t8.is_installed('pathlib')
    assert t8.is_installed('pdf')
    assert t8.is_installed('ping')
    assert t8.is_installed('requests')
    assert t8.is_installed('sqlalchemy')

    assert not t8.is_installed('ten8t')

def test_import_version():
    assert t8.__version__ != "unknown"

    #For now this only matches on the pattern of dd.dd.dd, since I don't bump the rev until later in the process.
    pattern = r"^\d{1,2}\.\d{1,2}\.\d{1,2}$"
    assert re.match(pattern,t8.__version__), f"Version '{t8.__version__}' does not match the expected format (e.g., '0.1.2', '10.11.12')"

