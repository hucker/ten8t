from src import ten8t


def check_suid11_a():
    """No RUID"""
    yield ten8t.Ten8tResult(status=True, msg="No RUID")


def check_suid12_a():
    """No RUID"""
    yield ten8t.Ten8tResult(status=True, msg="No RUID")
