from collections.abc import Callable
from functools import wraps
from typing import TypeVar

from .exceptions import NotSubclsError, NotClsError


_F = TypeVar("_F", bound=Callable)


def ensure_subcls_on_arg(expected: type, pos: int = 0) -> Callable[[_F], _F]:
    """
    Ensures, that the callable's argument at given position is a subclass of
    `expected`. If not, raises `NotSubclsError`(`TypeError`). If the argument
    is not a class at all, raises `NotClsError`(`TypeError`).
    """

    def _ensure_subcls_decorator_factory(f: _F) -> _F:
        @wraps(f)
        def _ensure_subcls_decorator(*args, **kwds):
            cls = args[pos]
            ensure_is_cls(cls)
            ensure_is_subcls_of(expected, cls)
            return f(*args, **kwds)

        return _ensure_subcls_decorator  # type: ignore

    return _ensure_subcls_decorator_factory


def ensure_is_subcls_of(expected: type, cls: type) -> None:
    if not issubclass(cls, expected):
        raise NotSubclsError(cls, expected)


def ensure_is_cls(x) -> None:
    if not isinstance(x, type):
        raise NotClsError(x)
