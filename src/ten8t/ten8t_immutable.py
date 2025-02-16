"""
Helper classes to support making environment variables with mutable values be less prone
to being changed by mistake.  We are under no presumption that we can stop people from
using a dynamic language.  These classes make the best effort to  prevent the user from
making edits to environment data that should be constant for the life of a rule
checking run.

THERE IS NO ASSURANCE THAT THIS WILL WORK IN ALL CASES. DON'T WRITE TO THE ENV VARIABLES!

"""

from .ten8t_exception import Ten8tException


class Ten8tEnvList(list):
    """
    Class representing a mutation-inhibited list. Mutational operations raise
    ten8t_exception.Ten8tException.

    Python being dynamic means forceful mutations can succeed. This class serves
    to prevent accidental changes by raising exceptions for mutating methods.

    Ideally, a copy is best to avoid mutation. But for large data sets, it's
    resource-demanding. ImmutableList protects large sets from unintended changes.
    """

    def __init__(self, *args):
        # super(Ten8tEnvList, self).__init__(*args)
        super().__init__(*args)

    def __setitem__(self, index, value):
        raise Ten8tException("Environment list does not support item assignment")

    def __delitem__(self, index):
        raise Ten8tException("Environment list doesn't support item deletion")

    def append(self, value):
        raise Ten8tException("Environment list is immutable, append is not supported")

    def extend(self, value):
        raise Ten8tException("Environment list is immutable, extend is not supported")

    def insert(self, index, value):
        raise Ten8tException("Environment list is immutable, insert is not supported")

    def remove(self, value):
        raise Ten8tException("Environment list is immutable, remove is not supported")

    def pop(self, index=-1):
        raise Ten8tException("Environment list is immutable, pop is not supported")

    def clear(self):
        raise Ten8tException("Environment list is immutable, clear is not supported")

    def sort(self, *args, **kwargs):
        raise Ten8tException("Environment list is immutable, sort is not supported")

    def reverse(self):
        raise Ten8tException("Environment list is immutable, reverse is not supported")


class Ten8tEnvDict(dict):
    """
    A class symbolizing a mutation-prohibited dictionary. Mutational operations raise
    a Ten8tException.

    Analogous to ImmutableList, Python's dynamic nature may allow forced mutations. This
    class prevents unintentional modifications to a dict object.
    """

    def __init__(self, *args, **kwargs):
        # super(Ten8tEnvDict, self).__init__(*args, **kwargs)
        super().__init__(*args, **kwargs)

    def __setitem__(self, key, value):
        raise Ten8tException("Environment dict does not support item assignment")

    def __delitem__(self, key):
        raise Ten8tException("Environment dict doesn't support item deletion")

    def pop(self, k, d=None):
        raise Ten8tException("Environment dict is immutable, pop is not supported")

    def popitem(self):
        raise Ten8tException("Environment dict is immutable, popitem is not supported")

    def clear(self):
        raise Ten8tException("Environment dict is immutable, clear is not supported")

    def update(self, other=(), **kwargs):
        raise Ten8tException("Environment dict is immutable, update is not supported")

    def setdefault(self, key, default=None):
        raise Ten8tException("Environment dict is immutable, setdefault is not supported")


class Ten8tEnvSet(frozenset):
    """ Support immutable sets using frozenset """
