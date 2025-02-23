"""Sample ten8t module with check functions"""

import time

from ten8t import TR, attributes


@attributes(tag="tag1", ruid="m2_f1", level=1, phase="proto")
def check_module2_func1():
    "Another always passing function"
    time.sleep(.5)
    yield TR(status=True, msg="Always passes")


@attributes(tag="tag2", ruid='m2_f2', level=2, phase="production")
def check_module2_func2():
    "THis thing always fails"
    time.sleep(.5)
    yield TR(status=False, msg="Always fails")


@attributes(tag="tag2", ruid='m2_f3', level=2, phase="production")
def check_module2_func3():
    "This thing always warns"
    time.sleep(.5)
    yield TR(status=True, warn_msg="Always warns and passes")


@attributes(tag="tag2", ruid='m2_f4', level=2, phase="production")
def check_module2_func4():
    "This thing always warns"
    time.sleep(.5)
    yield TR(status=False, warn_msg="Always warns and fails")
