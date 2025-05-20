# Dictionary of standard package installs
TEN8T_PACKAGES = {}


def _install(name: str, installed: bool = True) -> None:
    if installed:
        TEN8T_PACKAGES[name] = "Installed"
    else:
        TEN8T_PACKAGES[name] = "Not Installed"


def is_installed(name: str) -> bool:
    """Is a given package installed?"""
    return name in TEN8T_PACKAGES


def whats_installed(sep: str = ",") -> str:
    """Generate a printable list of installed packages."""
    return sep.join(installed_ten8t_packages())


def installed_ten8t_packages():
    """List of installed ten8t packages"""
    return sorted(TEN8T_PACKAGES.keys())
