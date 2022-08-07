from collections.abc import Callable
from dataclasses import dataclass
from typing import Any, NoReturn


def clsname(x) -> str:
    return type(x).__name__


Name = str
Value = Any


def raise_if(pred: bool, e: Exception) -> None:
    if not pred:
        raise e


def raise_if_lazy(pred: Callable[[], bool], e: Exception) -> None:
    if pred():
        raise e


@dataclass
class NonInitializableError(Exception):
    cls: type

    def __str__(self) -> str:
        return f"{type(self).__name__}: {self.cls.__name__}"


class NonInitClsMeta(type):
    def __call__(self, *_, **__) -> NoReturn:
        del _, __
        raise NonInitializableError(type(self))


class UnknownType(metaclass=NonInitClsMeta):
    ...
