"""
This module is used to check for RUID files in the system.
"""

from collections import Counter

from .ten8t_module import Ten8tModule
from .ten8t_package import Ten8tPackage


def module_ruids(module: Ten8tModule) -> list[str]:
    """get a list of all the RUIDS in a module"""
    return [function.ruid for function in module.check_functions]


def package_ruids(package: Ten8tPackage) -> list[str]:
    """get a list of all the RUIDS in a package"""
    ruids = []
    for module in package.modules:
        ruids.extend(module_ruids(module))
    return ruids


def empty_ruids(ruids: list[str]) -> bool:
    """Check if all ruids are empty"""
    return all((not ruid for ruid in ruids))


def valid_ruids(ruids: list[str]) -> bool:
    """Check if all ruids are valid"""
    return len(ruids) == len(set(ruids)) and "" not in ruids


def ruid_issues(ruids: list[str]) -> str:
    """
    Provide a message about the issues with the RUIDs in the package.

    An issue is defined as either duplicate RUIDs (excluding blank entries)
    or the presence of blank RUIDs. The returned message will list any
    duplicate RUIDs and indicate whether blank RUIDs are present.

    If no issues are found, the returned message will indicate this.
    """
    ruid_counts = Counter(ruids)
    duplicates = [
        ruid for ruid, count in ruid_counts.items() if count > 1 and ruid != ""
    ]
    blanks = "" in ruids

    issues = []
    if duplicates:
        issues.append(f"Duplicates: {', '.join(duplicates)}.")
    if blanks:
        if empty_ruids(ruids):
            issues.append("RUIDS are not used.")
        else:
            issues.append("Blank RUIDs are present.")

    msg = " ".join(issues) if issues else "No issues found."
    return msg
