from abc import ABC, abstractmethod
from dataclasses import InitVar, dataclass, field
from typing import Any, ClassVar, Generic, TypeVar, cast, final

from typing_extensions import Self
from weakref import ReferenceType, ref

from ._meta import SingletonMeta
from ..exceptions import (
    AbstractSingletonInitError,
    InvalidationError,
    NoInstanceError,
    ReinitError,
)


_AbstractSingletonCls = TypeVar("_AbstractSingletonCls", bound=SingletonMeta)
T = TypeVar("T")


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


@abstract_singleton
class SimpleSingleton(ABC, metaclass=SingletonMeta):
    @classmethod
    def get_instance(cls) -> Self:
        if (i := cls.maybe_get_instance()) is None:
            raise NoInstanceError(cls)
        else:
            return i

    @classmethod
    def maybe_get_instance(cls) -> Self | None:
        return cls._instance

    @classmethod
    def instance_exists(cls) -> bool:
        return cls.maybe_get_instance() is not None

    def __new__(cls: type[Self], *_, **__) -> Self:
        # The correct error when wrong arguments (or keywords) are given will
        # still be thrown, even if we do not care about them in __new__ method
        del _, __

        # vvv can be found in `SingletonMeta` - it is declared there, but the
        # implementation is injected by `abstract_singleton` decorator.
        if cls._is_abstract_singleton():
            raise AbstractSingletonInitError(cls)

        if cls.instance_exists():
            return cls._instance
        else:
            return cls._create_and_register_new_instance()

    @classmethod
    def _create_and_register_new_instance(cls) -> Self:
        # This has to be done this way, because otherwise weakref singletons
        # will lose the only one hard reference to the instance during
        # it very initialization
        new_instance = cls._create_new_instance()
        return cls._register_new_instance(new_instance)

    @final
    @classmethod
    def _create_new_instance(cls) -> Self:
        return super().__new__(cls)

    @classmethod
    def _register_new_instance(cls, i: Self) -> Self:
        cls._instance = i
        return i


@abstract_singleton
class NoImplicitReinitSingleton(SimpleSingleton, ABC):
    """
    Raises `ReinitError` on second initialization attempt.
    """

    def __new__(cls: type[Self], *args, **kwds) -> Self:
        if cls.instance_exists():
            raise ReinitError(cls)
        else:
            return super().__new__(cls, *args, **kwds)


_ExpIniSingClsT = TypeVar("_ExpIniSingClsT", bound=type["ExplicitReinitSingleton"])


def disable_invalidation_error(cls: _ExpIniSingClsT) -> _ExpIniSingClsT:
    """
    Disables raising InvalidationError, instance validity can still be checked
    with a method.
    """

    cls.__singleton_no_raise_invalidation__ = True
    return cls


@abstract_singleton
class ExplicitReinitSingleton(NoImplicitReinitSingleton, ABC):
    """
    Adds `reinit` method that invalidates all hard references and creates a new
    instance. Invalidated objects will raise InvalidationError when used (e.g.
    their attributes will be used). This will not invalidate already copied or
    referenced attributes of singletons, so use with caution. You can somehow
    solve this issue by wrapping the referenced attributes with `wrap_attr` or
    `wrap_attr_weak` - those return references, that can further be extended
    with their `forward_ref` methods. Each instance can check, whether it is
    valid, by calling `is_instance_valid` method.
    """

    # ? maybe create another clas above that does not raise InvalidationError

    @classmethod
    def reinit(cls, *args, **kwds) -> Self:
        cls._unregister_instance()
        new_instance = cls(*args, **kwds)
        return new_instance

    @classmethod
    def invalidate_singleton(cls, raise_invalidation=False) -> None:
        cls._unregister_instance()

        if raise_invalidation:
            raise InvalidationError(cls)

    def is_instance_valid(self) -> bool:
        return id(self) == id(type(self).maybe_get_instance())

    def wrap_attr(self, a: T) -> "SingletonInstanceFieldRef[Self, T]":
        return SingletonInstanceFieldRef(self, a)

    def wrap_attr_weak(self, a: T) -> "SingletonInstanceFieldRefWeak[Self, T]":
        return SingletonInstanceFieldRefWeak(self, a)

    @classmethod
    def _unregister_instance(cls) -> None:
        """
        Override to inject behaviour to `reinit` when the instance is being
        discarted.
        """

        cls._instance = None

    __singleton_no_raise_invalidation__: ClassVar[bool] = False

    def __getattribute__(self, __name: str) -> Any:
        # avoids RecursionError
        if __name == "is_instance_valid":
            return object.__getattribute__(self, __name)
        elif type(self).__singleton_no_raise_invalidation__ or self.is_instance_valid():
            return super().__getattribute__(__name)
        else:
            raise InvalidationError(type(self))


# ******************************************************************************
# * Types below are private (not exported inside __init__.py)

_SourceT = TypeVar("_SourceT", bound=ExplicitReinitSingleton)
_ToForwardT = TypeVar("_ToForwardT")
_RefT = TypeVar("_RefT", bound="AbstractSingletonInstanceFieldRef")


class AbstractSingletonInstanceFieldRef(ABC, Generic[_SourceT, T]):
    def __init__(self, _source: ExplicitReinitSingleton, _wrapped) -> None:
        super().__init__()
        self._source = _source
        self._wrapped = _wrapped
        self._source_t = type(_source)

    def __call__(self) -> T:
        return self.unwrap()

    def unwrap(self) -> T:
        self._guarantee_source_validity()
        return self._wrapped

    @abstractmethod
    def forward_ref(
        self, x: _ToForwardT
    ) -> "AbstractSingletonInstanceFieldRef[_SourceT, _ToForwardT]":
        ...

    def is_source_valid(self) -> bool:
        return self._maybe_get_source() is not None

    @abstractmethod
    def _maybe_get_source(self) -> _SourceT | None:
        ...

    def _forward_ref_as(self, refcls: type[_RefT], x) -> _RefT:
        self._guarantee_source_validity()
        return refcls(self._source, x)

    def _guarantee_source_validity(self) -> None:
        """
        Raises InvalidationError if the instance is not valid anymore.
        """

        if not self.is_source_valid():
            raise InvalidationError(self._source_t)


@dataclass(frozen=True)
class SingletonInstanceFieldRef(
    AbstractSingletonInstanceFieldRef, Generic[_SourceT, T]
):
    """
    Adds invalidation on `Singleton` instance field access on shallow level.
    You can wrap nested values by using `forward_ref` method.
    This is NOT a weakref.ReferenceType!
    """

    _source: _SourceT
    _wrapped: T
    _source_t: type[_SourceT] = field(init=False)

    def forward_ref(
        self, x: _ToForwardT
    ) -> "SingletonInstanceFieldRef[_SourceT, _ToForwardT]":
        return self._forward_ref_as(SingletonInstanceFieldRef, x)

    def forward_ref_weak(
        self, x: _ToForwardT
    ) -> "SingletonInstanceFieldRefWeak[_SourceT, _ToForwardT]":
        return self._forward_ref_as(SingletonInstanceFieldRefWeak, x)

    def _maybe_get_source(self) -> _SourceT:
        return self._source

    def __post_init__(self) -> None:
        object.__setattr__(self, "_source_t", type(self._source))


@dataclass(frozen=True)
class SingletonInstanceFieldRefWeak(
    AbstractSingletonInstanceFieldRef, Generic[_SourceT, T]
):
    # FIXME this is wrongly typed, in reality this type is correct only for
    # manual initialization, but later it can be a weak reference type
    _source: _SourceT
    _wrapped: T

    _source_t: type[_SourceT] = field(init=False)

    def forward_ref(
        self, x: _ToForwardT
    ) -> "SingletonInstanceFieldRefWeak[_SourceT, _ToForwardT]":
        return self._forward_ref_as(SingletonInstanceFieldRefWeak, x)

    def _maybe_get_source(self) -> _SourceT | None:
        assert isinstance(self._source, ReferenceType)
        return self._source()

    def __post_init__(self) -> None:
        # this dataclass is frozen, hence we must use object.__setattr__
        self_setattr = lambda name, val: object.__setattr__(self, name, val)
        set_source_t = lambda source: self_setattr("_source_t", type(source))

        instance_or_ref = self._source

        if isinstance(instance_or_ref, ReferenceType):
            instance = instance_or_ref()
            if instance is None:
                raise InvalidationError(
                    type(None), "could not even initialize the weak reference"
                )
            else:
                # only set _source_t
                set_source_t(instance)
        else:
            instance = self._source
            self_setattr("_source_ref", ref(instance))
            set_source_t(instance)
