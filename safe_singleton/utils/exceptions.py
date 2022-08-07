from abc import ABC
from dataclasses import InitVar, dataclass, field
from typing import Any

from .exception_utils import pretty_error
from .pure_abc import PureAbcException


@dataclass
class PrettyError(PureAbcException, ABC):
    """
    Provides uniform string conversion of its subclasses.
    """

    # Not default, because it will mess inheriting classes. It is an abstract
    # class anyway. Subclasses can make overwrite it, thus make it default to
    # something or be not required for `__init__`.
    msg: str

    def __str__(self) -> str:
        return pretty_error(self)


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
