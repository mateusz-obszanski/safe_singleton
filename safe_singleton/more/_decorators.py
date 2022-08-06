from typing import TypeVar

from ._meta import SingletonMeta
from ._base import EnsureInitSingleton, ExplicitReinitSingleton
from ._misc import ensure_subcls_dec

_AbstractSingletonCls = TypeVar("_AbstractSingletonCls", bound=SingletonMeta)
_EnsIniSingT = TypeVar("_EnsIniSingT", bound=type[EnsureInitSingleton])
_ExpIniSingClsT = TypeVar("_ExpIniSingClsT", bound=type[ExplicitReinitSingleton])


def abstract_singleton(
    __cls: _AbstractSingletonCls,
) -> _AbstractSingletonCls:
    """
    Injects necessary methods into abstract singleton.
    """

    @classmethod
    def _is_abstract_singleton(cls) -> bool:
        return cls is __cls

    __cls._is_abstract_singleton = _is_abstract_singleton  # type: ignore

    return __cls


@ensure_subcls_dec(ExplicitReinitSingleton)
def no_invalidation_error(cls: _ExpIniSingClsT) -> _ExpIniSingClsT:
    """
    Disables raising InvalidationError, instance validity can still be checked
    with a method.
    """

    cls.__singleton_no_raise_invalidation__ = True
    return cls


@ensure_subcls_dec(EnsureInitSingleton)
def no_ensure_init(cls: _EnsIniSingT) -> _EnsIniSingT:
    """
    Disables automatic `EnsureInitSingleton`'s or its subclass' `__init__`
    invocation (it is called even if there is no `super` call inside subclass'
    `__init__`).
    """

    cls.__singleton_ensure_init__ = False
    return cls
