from abc import ABC
from dataclasses import dataclass
from typing import final

from .utils import clsname


@dataclass
class SingletonError(Exception, ABC):
    """
    Abstract `Singleton` error
    """

    cls: type
    msg: str = ""

    def __str__(self) -> str:
        msg = self.msg
        suffix = f":{msg}" if msg else ""
        return f"{clsname(self)}{suffix}"


@final
class AbstractSingletonInitError(SingletonError, TypeError):
    """
    Raised, when one of abstract Singleton classes are being initialized without
    subclassing.
    """


@final
class ReinitError(SingletonError):
    """
    Raised on implicit reinitialization of instance
    """

    def __post_init__(self) -> None:
        self.msg = (
            f"attempted to implicitly reinitialize singleton `{self.cls.__name__}`"
        )


@final
class NoInstanceError(SingletonError):
    """
    Raised when instance is expected to be initialized but there is none
    """


@final
class InvalidationError(SingletonError):
    """
    Raised when singleton has been reinitialized anywhere in the code.
    """
