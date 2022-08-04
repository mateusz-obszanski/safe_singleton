from collections.abc import Callable
from functools import reduce
from typing import Any, Generic, ParamSpec, TypeVar

_T = TypeVar("_T")
_R = TypeVar("_R")
_ArgTs = ParamSpec("_ArgTs")
_ReturnT = TypeVar("_ReturnT")


class compose(Generic[_ArgTs, _ReturnT]):
    def __init__(
        self, f1: Callable[_ArgTs, _T], f2: Callable[[_T], Any], /, *fs: Callable
    ) -> None:
        super().__init__()
        self.fs = (f1, f2, *fs)
        self._f1 = f1
        self._fs_tail = (f2, *fs)

    # This is a class and not a function for generic return type
    def __call__(self, *args: _ArgTs.args, **kwds: _ArgTs.kwargs) -> _ReturnT:
        return reduce(self._call_f, self._fs_tail, self._f1(*args, **kwds))  # type: ignore

    @staticmethod
    def _call_f(f: Callable[[_T], _R], prev_result: _T) -> _R:
        return f(prev_result)
