from abc import ABC, ABCMeta
from dataclasses import dataclass, field
from functools import wraps
from itertools import dropwhile
from typing import TypeGuard, cast, final
from typing_extensions import Self

from ..exception_utils import pretty_error
from ._utils import is_pure_abc


class PureAbcMeta(ABCMeta, type):
    """
    Metaclass for abstract base classes that do not contain `abstractmethod`s,
    but are not meant to be initialized.
    """

    def is_pure_abc(cls: Self, __cls: Self | None = None) -> TypeGuard[ABC]:
        """
        The `__cls` argument is only for utilizing `TypeGuard` and should be
        in fact the implicit `cls`.
        """

        # The whole __cls for TypeGuard thing is an overkill and additionally
        # annotation both cls and __cls as Self probably is enough, because
        # static type-checkers will show if they are not the same, but whatever.
        if __cls is None:
            __cls = cls
        if __cls is not cls:
            raise ClsIdentityError(cast(type[ABC], __cls), expected=cls)
        return is_pure_abc(__cls)

    def assure_is_pure_abc(cls) -> None:
        if not cls.is_pure_abc():
            raise IsNotPureAbcError(cast(type[ABC], cls))

    def assure_is_not_pure_abc(cls) -> None:
        if cls.is_pure_abc():
            raise IsPureAbcError(cast(type[ABC], cls))

    def __init__(cls, *_, **__) -> None:
        del _, __

        original_init = cls.__init__

        # Wrapping __new__ does not work, because calling object.__new__ directly
        # is not permitted

        @wraps(original_init)
        def __init__(self, *args, **kwds):
            _cls = type(self)

            if is_pure_abc(_cls):
                raise PureAbcInitError(cast(type[ABC], _cls))
            else:
                if original_init is object.__init__:
                    args = ()
                    kwds = {}

                return original_init(self, *args, **kwds)

        setattr(cls, cls.__init__.__name__, __init__)


@dataclass(frozen=True)
class PureAbcError(Exception, metaclass=PureAbcMeta):
    msg: str = field(init=False)
    cls: type[ABC]

    def __str__(self) -> str:
        return pretty_error(self)

    def __post_init__(self) -> None:
        object.__setattr__(self, "msg", self.cls.__name__)


class IsPureAbcError(PureAbcError):
    """
    Raised, when it cannot be assured, that the cls is a pure abstract class.
    """


class IsNotPureAbcError(PureAbcError):
    """
    The opposite of `IsPureAbcError`.
    """


class PureAbcInitError(PureAbcError):
    """
    Raised, when pure ABC is being initialized.
    """


@final
@dataclass(frozen=True)
class ClsIdentityError(PureAbcError):
    """
    Raised when pure abc's `is_pure_abc` `classmethod` is called with an
    argument for sake of using a `TypeGuard`, but classes do not match.
    """

    expected: type
