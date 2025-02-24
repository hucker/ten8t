"""DocString for check_simple1"""
from src import ten8t as t8


def check_hello():
    """DocString for check_hello"""
    yield t8.Ten8tResult(status=True, msg="Result check_hello")
