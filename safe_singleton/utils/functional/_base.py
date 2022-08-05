from collections.abc import Callable
from functools import reduce
from typing import Any, Generic, ParamSpec, TypeVar

_T = TypeVar("_T")
_R = TypeVar("_R")
_ArgTs = ParamSpec("_ArgTs")
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


class composed(Generic[_ArgTs, _ReturnT]):
    # This is a class and not a function in order to specify generic return type
    def __init__(
        self, f1: Callable[_ArgTs, _T], f2: Callable[[_T], Any], /, *fs: Callable
    ) -> None:
        super().__init__()
        self.fs = (f1, f2, *fs)
        self._f1 = f1
        self._fs_tail = (f2, *fs)

    def __call__(self, *args: _ArgTs.args, **kwds: _ArgTs.kwargs) -> _ReturnT:
        return reduce(call_on, self._fs_tail, self._f1(*args, **kwds))  # type: ignore
