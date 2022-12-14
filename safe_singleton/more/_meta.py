from abc import ABCMeta, abstractmethod
from functools import wraps
from typing import TypeVar

from ..exceptions import AbstractIsAbstractSingletonMethodNotImplementedError


# Since in Python everything is a class, including classes, they too can be
# initialized in a custom way - this is what metaclasses are supposed to do.
# They are "types of types" - each method within a metaclass is like
# a classmethod in a normal one.
class SingletonMeta(ABCMeta, type):
    def __init__(cls, *_, **__) -> None:
        del _, __
        # This will not be overwritten, because the __init__ is for a class,
        # thus called at the moment of class definition.
        cls._instance = None
        # Metaclass' __init__ is called for each child, not only the first that
        # specifies it as its metaclass. This makes auto-generating
        # `_is_abstract_singleton` here impossible.

    # Unfortunately, marking this an abstractmethod does nothing ¯\_(ツ)_/¯,
    # but the intent is clearer. It is generated by a `abstract_singleton`
    # decorator.
    @abstractmethod
    def _is_abstract_singleton(cls) -> bool:
        raise AbstractIsAbstractSingletonMethodNotImplementedError(cls)


_AbstractSingletonCls = TypeVar("_AbstractSingletonCls", bound=SingletonMeta)


def abstract_singleton(
    __cls: _AbstractSingletonCls,
) -> _AbstractSingletonCls:
    """
    Injects necessary methods into abstract singleton.
    """

    original_is_abstract_singleton_method = __cls._is_abstract_singleton

    # Without `classmethod`, Python shouts that it needs `cls` argument, but it
    # it was not provided. If `wraps` is above `classmethod`, it shouts again,
    # that some property is read-only.
    @classmethod
    @wraps(original_is_abstract_singleton_method)
    def _is_abstract_singleton(cls) -> bool:
        return cls is __cls

    setattr(
        __cls, original_is_abstract_singleton_method.__name__, _is_abstract_singleton
    )

    return __cls
