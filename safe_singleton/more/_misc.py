"""
Miscelaneous internal utilities.
"""

from collections.abc import Callable
from typing import Generic, Protocol, TypeVar


_Cls = TypeVar("_Cls", bound=type)


class _ClsDecorator(Protocol, Generic[_Cls]):
    def __call__(self, cls: _Cls) -> _Cls:
        ...


def ensure_subcls_dec(
    expected: _Cls,
) -> Callable[[_ClsDecorator[_Cls]], _ClsDecorator[_Cls]]:
    def _ensure_subcls_factory(d: _ClsDecorator) -> _ClsDecorator:
        def _wrapped_cls_decorator(cls: _Cls) -> _Cls:
            _ensure_subcls(expected, cls)
            return d(cls)

        return _wrapped_cls_decorator

    return _ensure_subcls_factory


def _ensure_subcls(expected: type, cls: type) -> None:
    if not issubclass(cls, expected):
        raise TypeError(
            f"expected {expected.__name__} class or its subclass, got {cls.__name__}"
        )
