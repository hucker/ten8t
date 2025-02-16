"""DocString for check_dec"""
from src import ten8t

"""
Test that functions are skipped with the skip flag.
"""


@ten8t.attributes(skip=True)
def check_skip():
    """DocString for skip"""
    yield ten8t.Ten8tResult(status=True, msg="Result check_dec1")


@ten8t.attributes(skip=False)
def check_no_skip():
    """DocString for skip"""
    yield ten8t.Ten8tResult(status=True, msg="Result check_dec2")
