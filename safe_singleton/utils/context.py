from contextlib import contextmanager
from collections.abc import Callable, Mapping
from typing import Any, TypeVar


_T = TypeVar("_T")


@contextmanager
def at_exit(f: Callable):
    try:
        yield
    finally:
        f()


@contextmanager
def set_del_attr(
    obj: _T, name: str, val: Any, setter: Callable[[_T, str, Any], Any] | None = None
):
    setter = setattr if setter is None else setter

    try:
        yield setter(obj, name, val)
    finally:
        try:
            delattr(obj, name)
        except Exception:
            pass


@contextmanager
def set_enter_set_exit(
    obj: _T,
    name: str,
    val_start: Any,
    val_exit: Any,
    setter: Callable[[_T, str, Any], Any] | None = None,
):
    setter = setattr if setter is None else setter

    try:
        yield setter(obj, name, val_start)
    finally:
        setter(obj, name, val_exit)


@contextmanager
def build_contextmanager(
    do_enter: Callable,
    do_exit: Callable,
    exc_handler_map: Mapping[type[Exception], Callable[[Exception], Any]],
):
    try:
        yield do_enter()
    except Exception as e:
        handler = exc_handler_map.get(type(e))
        if handler is None:
            raise
        else:
            handler(e)
    finally:
        do_exit()
