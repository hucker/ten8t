from src import ten8t


@ten8t.attributes(ruid="suid21")
def check_suid11_x():
    """Check RUID"""
    yield ten8t.Ten8tResult(status=True, msg="RUID 21")


@ten8t.attributes(ruid="suid22")
def check_suid12_x():
    """Check RUID"""
    yield ten8t.Ten8tResult(status=True, msg="RUID 22")
