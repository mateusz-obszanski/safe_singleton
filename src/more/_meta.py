from abc import ABCMeta, abstractmethod
from typing import TypedDict


class MetaClassInitDict(TypedDict):
    __module__: str
    __qualname__: str


# Since in Python everything is a class, including classes, they too can be
# initialized in a custom way - this is what metaclasses are supposed to do.
# They are "types of types" - each method within a metaclass is like
# a classmethod in a normal one.


class SingletonMeta(ABCMeta, type):
    def __init__(
        cls, name: str, bases: tuple[type, ...], dct: MetaClassInitDict
    ) -> None:
        del name, bases, dct
        # This will not be overwritten, because the __init__ is for a class,
        # thus called at the moment of class definition.
        cls._instance = None
        # Metaclass' __init__ is called for each child, not only the first that
        # specifies it as its metaclass. This makes auto-generating
        # `_is_abstract_singleton` here impossible.

    # Unfortunately, marking this as abstract does nothing ¯\_(ツ)_/¯
    # but the intent is clearer. It is generated by a decorator
    @abstractmethod
    def _is_abstract_singleton(cls) -> bool:
        ...
