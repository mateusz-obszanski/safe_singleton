from abc import abstractmethod
from collections.abc import Callable, Iterable, Sequence
from functools import wraps
from typing import Any, Generic, Protocol, TypeVar, overload


_F = TypeVar("_F", bound=Callable)
_Method = TypeVar("_Method", bound=Callable)
_Decorator = Callable


def clsname(x) -> str:
    return type(x).__name__


def decorate(d: _Decorator, f: _F, *d_args, **d_kwargs) -> _F:
    """
    Simply decorates `f` with `d`.
    """

    # just to be sure, should be done inside `d` anyway
    d = wraps(f)(d)

    return d(f, *d_args, **d_kwargs)


def multidecorate(ds: Sequence[_Decorator], f: _F) -> _F:
    """
    Decorate `f` with decorators `ds` in reversed order, equivalent to:

    ```
    @d1
    @d2
    ...
    @dn
    def f(...
    ```
    """

    return multidecorate_left(reversed(ds), f)


def multidecorate_left(ds: Iterable[_Decorator], f: _F) -> _F:
    """
    Decorate `f` with decorators `ds` equivalent to:

    ```
    multidecorate(reversed([d1, d2, ..., dn]), f)
    ```

    or

    ```
    @dn
    ...
    @d2
    @d1
    def f(...
    ```
    """

    for d in ds:
        f = decorate(d, f)

    return f


def abstractclassmethod(m: _Method) -> _Method:
    """
    Shorthand, written because the standard version is deprecated.
    """

    return multidecorate((abstractmethod, classmethod), m)
