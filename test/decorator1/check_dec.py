"""
DocString for check_dec

This has two check functions with different prefixes check_/rule_, this allows
us to verify that our auto loading of check functions is working.
"""
from src.ten8t import TR, attributes


@attributes(tag='tag1', level=1)
def check_dec():
    """DocString for check_dec"""
    yield TR(status=True, msg="Result check_dec")


@attributes(tag='tag1', level=1)
def rule_dec():
    yield TR(status=True, msg="Result rule_dec")
