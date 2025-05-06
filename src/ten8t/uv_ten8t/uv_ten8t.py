#!/user/bin/env -S uv run --script
# /// script
# dependencies = ["ten8t>=0.0.22"]
# ///

"""Example of a checker run under uv run"""

import ten8t as t8
from ten8t import Ten8tChecker, Ten8tResult, cwd_here

cwd_here(__file__)


def check_1():
    """ Always returns pass """
    return t8.Ten8tResult(status=True, msg="This test worked.")  # pragma no cover


def check_2():
    """ List of filenames """
    yield from t8.rule_paths_exist(paths=["uv_ten8t.py"])


def check_3():
    """ String of file names """
    yield from t8.rule_paths_exist(paths="uv_ten8t.py")


def check_4():
    """ Multiple paths in string """
    yield from t8.rule_paths_exist(paths="uv_ten8t.py .")


def check_5():
    """ Check multiple URLs """
    yield from t8.rule_url_200(urls="http://www.google.com http://www.microsoft.com")


ch = Ten8tChecker(check_functions=[check_1, check_2, check_3, check_4, check_5])

for result in ch.yield_all():  # type: Ten8tResult
    if result.status:
        print(f"Pass: Function:{result.func_name} - {result.msg_rendered}")
    else:
        print(f"Fail: Function:{result.func_name} - {result.msg_rendered}")

print(f"Final result: {ch.pass_count=} {ch.fail_count=} ")
