from collections.abc import Callable, Iterable, Sequence
from functools import wraps
from typing import TypeVar, cast

_FunctionT = TypeVar("_FunctionT", bound=Callable)
_SimpleDecorator = Callable[[Callable], Callable]
_Decorator = Callable[..., Callable]


def decorate(d: _Decorator, f: _FunctionT, *d_args, **d_kwargs) -> _FunctionT:
    """
    Simply decorates `f` with `d`.
    """

    # just to be sure, should be done inside `d` anyway
    d = wraps(f)(d)
    wrapped = d(f, *d_args, **d_kwargs)

    return cast(_FunctionT, wrapped)


def multidecorate(ds: Sequence[_Decorator], f: _FunctionT) -> _FunctionT:
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


def multidecorate_left(ds: Iterable[_SimpleDecorator], f: _FunctionT) -> _FunctionT:
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
