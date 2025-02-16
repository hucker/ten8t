from src.ten8t import TR, attributes


@attributes(ruid="suid21")
def check_suid21_d():
    """Check RUID"""
    yield TR(status=True, msg="RUID 21")


@attributes(ruid="suid22")
def check_suid122_d():
    """Check RUID"""
    yield TR(status=True, msg="RUID 22")


@attributes(ruid="suid22")
def check_suid23_d():
    """Check RUID"""
    yield TR(status=True, msg="RUID 23")
