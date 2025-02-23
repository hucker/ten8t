"""Sample Ten8t module with check functions"""

import time

from ten8t import TR, attributes


@attributes(tag="tag1", ruid="m1_f1", level=1, phase="proto")
def check_module1_func1():
    """ Simple always passing function"""
    time.sleep(.5)
    yield TR(status=True, msg="Always passes")


@attributes(tag="tag2", ruid="m1_f2", level=2, phase="proto")
def check_module1_func2():
    """ Simple always Failing Function"""
    time.sleep(.5)
    yield TR(status=True, msg="Always passes")


@attributes(tag="tag3", ruid="m1_f3", level=3, phase="production")
def check_module1_func3():
    """ Skips because flag set"""
    time.sleep(.5)
    yield TR(status=False, msg="Always passes", skipped=True)
