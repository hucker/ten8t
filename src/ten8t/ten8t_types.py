import datetime as dt
import pathlib
from typing import Sequence, TypeAlias

# Type aliases.
# Note: the *OrNone are meant to be constructors that allow a None value to be passed
#       that code will take care to convert to a [] or a ''
BoolOrNone: TypeAlias = bool | None
"""Type alias for a boolean or None."""

DateTimeOrNone: TypeAlias = dt.datetime | None
""" Type alias for a datetime or None. """

ListOrNone: TypeAlias = list | None
"""Type alias for a list or None."""

StrOrNone: TypeAlias = str | None
"""Type alias for a string or None."""

StrList: TypeAlias = Sequence[str]
"""Type alias for a sequence of strings."""

StrListOrNone: TypeAlias = StrList | StrOrNone
"""Type alias for a sequence of strings or None."""

IntOrNone: TypeAlias = int | None
"""Type alias for an integer or None."""

IntList: TypeAlias = Sequence[int]
"""Type alias for a sequence of integers."""

IntListOrNone: TypeAlias = IntList | IntOrNone
"""Type alias for a sequence of integers or None."""

FloatOrNone: TypeAlias = float | None
"""Type alias for a float or None."""

FloatList: TypeAlias = Sequence[float]
"""Type alias for a sequence of floats."""

FloatListOrNone: TypeAlias = FloatList | FloatOrNone
"""Type alias for a sequence of floats or None."""

StrOrPath: TypeAlias = str | pathlib.Path
StrOrPathOrNone: TypeAlias = StrOrPath | None
StrOrPathList: TypeAlias = Sequence[StrOrPath]
StrOrPathListOrNone: TypeAlias = StrOrPathList | None

PathList: TypeAlias = Sequence[pathlib.Path]
