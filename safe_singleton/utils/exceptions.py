from abc import ABC
from dataclasses import InitVar, dataclass, field
from typing import Any

from ._base import clsname


@dataclass
class PrettyError(Exception, ABC):
    """
    Provides uniform string conversion of its subclasses.
    """

    # Not default, because it will mess inheriting classes. It is an abstract
    # class anyway. Subclasses can make overwrite it, thus make it default to
    # something or be not required for `__init__`.
    msg: str

    def __str__(self) -> str:
        msg = self.msg
        suffix = f":{msg}" if msg else ""
        return f"{clsname(self)}{suffix}"


@dataclass
class CalledNonInitCallableError(PrettyError, TypeError):
    """
    Raised, when callable object that is not supposed to be initialized has been
    called (it should have a `classmethod` `__call__`).
    """

    instance: InitVar[Any]
    callee: type = field(init=False)
    msg: str = field(init=False)

    def __post_init__(self, instance) -> None:
        callee = type(instance)
        self.callee = callee
        self.msg = f"{callee.__name__} is not initializable"


@dataclass
class NotSubclsError(PrettyError, TypeError):
    cls: type
    expected: type
    msg: str = field(init=False)

    def __post_init__(self) -> None:
        self.msg = f"expected {self.expected.__name__}, got {self.cls.__name__}"


class NotClsError(PrettyError, TypeError):
    x: Any
    msg: str = field(init=False)

    def __post_init__(self) -> None:
        self.msg = "provided object is not a class"
