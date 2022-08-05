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


@final
class UnregisterError(SingletonError):
    """
    Raised on exception during unregistration of singleton's instance during
    __init__ exception handling.
    """


# vvv does not inherit from `UnregisterError`, because it SHOULD NOT be treated
# and caught as such - it is a critical case after all
@final
@dataclass
class CriticalUnregisterError(SingletonError):
    """
    Critical error - could not clean up after singleton instance initialization.
    """

    errors: tuple[Exception, ...] = ()

    def __str__(self) -> str:
        prefix = super().__str__()
        return f"{prefix} Exception was caoused by following errors: {self.errors}."
