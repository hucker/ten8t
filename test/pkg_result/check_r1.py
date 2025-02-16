from src.ten8t import Ten8tResult, attributes


@attributes(ruid="pass11", tag='tag1')
def check_ruid11():
    """Check RUID"""
    yield Ten8tResult(status=True, msg="RUID 11")


@attributes(ruid="fail12", tag='tag1')
def check_ruid12():
    """Check RUID"""
    yield Ten8tResult(status=False, msg="RUID 12")


@attributes(ruid="skip_none", tag='tag1')
def check_ruid13():
    """Check RUID"""
    yield Ten8tResult(status=None, msg="RUID 13")


@attributes(ruid="skip_flag", tag='tag2')
def check_ruid14():
    """Check RUID"""
    yield Ten8tResult(status=True, msg="RUID 14", skipped=True)


@attributes(ruid="warning", tag='tag2')
def check_ruid15():
    """Check RUID"""
    yield Ten8tResult(status=True, msg="RUID 15", warn_msg="This is a warning")


@attributes(ruid="info", tag='tag2')
def check_ruid16():
    """Check RUID"""
    yield Ten8tResult(status=True, msg="RUID 16", skipped=True, info_msg="This is an info")


@attributes(ruid="blank_msg", tag='tag3')
def check_ruid17():
    """Check RUID"""
    yield Ten8tResult(status=True, msg="", skipped=True, info_msg="")
