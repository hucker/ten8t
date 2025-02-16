from src import ten8t


@ten8t.attributes(ruid="suid11")
def check_suid11_x():
    """Check RUID"""
    yield ten8t.Ten8tResult(status=True, msg="RUID 11")


@ten8t.attributes(ruid="suid12")
def check_suid12_x():
    """Check RUID"""
    yield ten8t.Ten8tResult(status=True, msg="RUID 12")
