"""DocString for check_dec"""
from src.ten8t import TR, attributes


@attributes(tag='tag1', level=1)
def check_dec():
    """DocString for check_dec"""
    yield TR(status=True, msg="Result check_dec")
