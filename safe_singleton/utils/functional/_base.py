from collections.abc import Callable, Iterator
from functools import reduce
from itertools import chain
from typing import Any, Generic, ParamSpec, TypeVar

_T = TypeVar("_T")
_R = TypeVar("_R")
_LastT = TypeVar("_LastT")
_ReturnT = TypeVar("_ReturnT")

_P = ParamSpec("_P")


def call(f: Callable[_P, _R], *args: _P.args, **kwds: _P.kwargs) -> _R:
    return f(*args, **kwds)


def lazy_call(
    f: Callable[_P, _R], *args: _P.args, **kwds: _P.kwargs
) -> Callable[[], _R]:
    return lambda: f(*args, **kwds)


def call_on(x: _T, f: Callable[[_T], _R]) -> _R:
    return f(x)


def lazy_call_on(x: _T, f: Callable[[_T], _R]) -> Callable[[], _R]:
    return lambda: f(x)


class call_chain(Generic[_P, _LastT]):
    def __init__(self, f1: Callable[_P, Any], f2: Callable, /, *fs: Callable) -> None:
        self._f1 = f1
        self._f2 = f2
        self._fs_tail = fs

    def __call__(self, *args: _P.args, **kwds: _P.kwargs) -> _LastT:
        self._f1(*args, **kwds)

        fs = self._fs_tail

        if not fs:
            return self._f2()
        else:
            *fs, f_last = fs

            for f in fs:
                f()

            return f_last()

    def __iter__(self) -> Iterator[Callable]:
        return chain((self._f1, self._f2), self._fs_tail)

    def to_list(self) -> list[Callable]:
        return list(self)

    def to_tuple(self) -> tuple[Callable, ...]:
        return tuple(self)


class composed(Generic[_P, _ReturnT]):
    """
    Lazy function composition.
    """

    # This is a class and not a function in order to specify generic return type
    def __init__(
        self, f1: Callable[_P, _T], f2: Callable[[_T], Any], /, *fs: Callable
    ) -> None:
        super().__init__()
        self._f1 = f1
        self._fs_tail = (f2, *fs)

    def __call__(self, *args: _P.args, **kwds: _P.kwargs) -> _ReturnT:
        return reduce(call_on, self._fs_tail, self._f1(*args, **kwds))  # type: ignore

    def __iter__(self) -> Iterator[Callable]:
        return chain((self._f1,), self._fs_tail)

    def to_list(self) -> list[Callable]:
        return list(self)

    def to_tuple(self) -> tuple[Callable]:
        return tuple(self)
