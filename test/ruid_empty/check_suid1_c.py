from src import ten8t as t8


def check_suid11_a():
    """No RUID"""
    yield t8.Ten8tResult(status=True, msg="No RUID")


def check_suid12_a():
    """No RUID"""
    yield t8.Ten8tResult(status=True, msg="No RUID")
