from src import ten8t as t8


@t8.attributes(ruid="suid21")
def check_suid11_x():
    """Check RUID"""
    yield t8.Ten8tResult(status=True, msg="RUID 21")


@t8.attributes(ruid="suid22")
def check_suid12_x():
    """Check RUID"""
    yield t8.Ten8tResult(status=True, msg="RUID 22")
