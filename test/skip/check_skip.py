"""DocString for check_dec"""
from src import ten8t as t8

"""
Test that functions are skipped with the skip flag.
"""


@t8.attributes(skip=True)
def check_skip():
    """DocString for skip"""
    yield t8.Ten8tResult(status=True, msg="Result check_dec1")


@t8.attributes(skip=False)
def check_no_skip():
    """DocString for skip"""
    yield t8.Ten8tResult(status=True, msg="Result check_dec2")
