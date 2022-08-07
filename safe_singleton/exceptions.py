from abc import ABC
from dataclasses import dataclass, field
from typing import final

# vvv for export
from .utils.exceptions import NotClsError, NotSubclsError, PrettyError


@dataclass
class SingletonError(PrettyError, ABC):
    """
    Abstract `Singleton` error
    """

    cls: type
    msg: str = field(init=False)
    reason: str = field(init=False, default="")

    def __post_init__(self) -> None:
        suffix = f" ({self.reason})" if self.reason else ""
        self.msg = f"{self.cls.__name__}{suffix}"


@final
class AbstractSingletonInitError(SingletonError, TypeError):
    """
    Raised, when one of abstract Singleton classes are being initialized without
    subclassing.
    """


# TypeError - like for abstract base classes that do not override abstract
# methods before initialization
@final
class AbstractIsAbstractSingletonMethodNotImplementedError(
    SingletonError, NotImplementedError, TypeError
):
    """
    Raised, when `_is_abstract_singleton` abstract classmethod has not been
    overriden before call.
    """


@final
class ImplicitReinitError(SingletonError):
    """
    Raised on implicit reinitialization of instance
    """


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
class NoAttrError(SingletonError, AttributeError):
    attr_name: str

    def __post_init__(self) -> None:
        assert self.attr_name
        self.reason = self.attr_name
        return super().__post_init__()


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

    def __post_init__(self) -> None:
        self.reason = f"caused by following errors: {self.errors}"
        super().__post_init__()
