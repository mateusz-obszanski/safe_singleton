from abc import ABC, abstractmethod
from collections.abc import Callable
from dataclasses import dataclass, field
from functools import wraps
from typing import Any, ClassVar, Generic, TypeGuard, TypeVar, final
from weakref import ReferenceType, ref

from typing_extensions import Self

from ..exceptions import (
    AbstractSingletonInitError,
    CriticalUnregisterError,
    ImplicitReinitError,
    InvalidationError,
    NoAttrError,
    NoInstanceError,
)
from ._meta import SingletonMeta, abstract_singleton
from ..utils import raise_if
from ..utils.context import at_exit, set_del_attr
from ..utils.decorators import ensure_subcls_on_arg
from ..utils.functional import call_chain


T = TypeVar("T")
ClsFlag = ClassVar[bool]


@abstract_singleton
class SimpleSingleton(ABC, metaclass=SingletonMeta):
    """
    The most basic singleton type
    """

    # `classmethod`s are here and not in a metaclass, because `Self` would be
    # unavailable there.

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

    def __copy__(self) -> Self:
        return self

    def __deepcopy__(self) -> Self:
        return self

    def __new__(cls, *args, **kwds) -> Self:
        # The correct error when wrong arguments (or keywords) are given will
        # still be thrown, even if we do not care about them in __new__ method.

        # vvv can be found in `SingletonMeta` - it is declared there, but the
        # implementation is injected by `abstract_singleton` decorator.
        if cls._is_abstract_singleton():
            raise AbstractSingletonInitError(cls)

        if cls.instance_exists():
            return cls._instance
        else:
            return cls._create_and_register_new_instance(args, kwds)

    @classmethod
    def _create_and_register_new_instance(cls, args: tuple, kwds: dict) -> Self:
        # This has to be done this way, because otherwise weakref singletons
        # will lose the only one hard reference to the instance during
        # it very initialization.
        new_instance = cls._create_new_instance(args, kwds)
        return cls._register_new_instance(new_instance)

    @final
    @classmethod
    def _create_new_instance(cls, args: tuple, kwds: dict) -> Self:
        del args, kwds
        return super().__new__(cls)

    @classmethod
    def _register_new_instance(cls, new_instance: Self) -> Self:
        cls._instance = new_instance
        return new_instance


@abstract_singleton
class NoImplicitReinitSingleton(SimpleSingleton, ABC):
    """
    Raises `ReinitError` on second initialization attempt.
    """

    def __new__(cls, *args, **kwds) -> Self:
        if cls.instance_exists():
            raise ImplicitReinitError(cls)
        else:
            return super().__new__(cls, *args, **kwds)


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

    __singleton_no_raise_invalidation__: ClsFlag = False

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

    def __getattribute__(self, __name: str) -> Any:
        cls = type(self)

        # avoids RecursionError
        if __name == cls.is_instance_valid.__name__:
            return object.__getattribute__(self, __name)
        elif cls.__singleton_no_raise_invalidation__ or self.is_instance_valid():
            return super().__getattribute__(__name)
        else:
            raise InvalidationError(cls)


@abstract_singleton
class EnsureInitSingleton(ExplicitReinitSingleton, ABC):
    """
    Ensures that its `__init__` method has been called no matter what - it can
    be disabled with `no_ensure_init` decorator. Use, when other packages e.g.
    those with dataclass-ish behaviour mess up Your objects.
    """

    __singleton_ensure_init__: ClsFlag = True
    __singleton_initialized__: ClsFlag = False
    __singleton_is_init_wrapped__: ClsFlag = False

    def __new__(cls, *args, **kwds) -> Self:
        instance = super().__new__(*args, **kwds)

        if not cls.__singleton_is_init_wrapped__ and cls.__singleton_ensure_init__:
            cls._wrap_init()

        return instance

    @classmethod
    def _wrap_init(cls) -> None:
        super_init = cls.__base__.__init__
        child_init = cls.__init__

        @wraps(cls.__init__)
        def __init__(self: Self, *args, **kwds) -> None:
            try:
                if not cls.__singleton_initialized__:
                    super_init(self, *args, **kwds)
                child_init(self, *args, **kwds)
            except Exception as e_init:
                try:
                    cls._unregister_instance()
                except Exception as e_unregister:
                    cls._critical_unregister_attempt(e_init, e_unregister)
                    raise e_unregister from e_init

            type(self).__singleton_initialized__ = True

        cls.__init__ = __init__

    @classmethod
    def _unregister_instance(cls) -> None:
        super()._unregister_instance()
        cls.__singleton_initialized__ = False

    @classmethod
    def _critical_unregister_attempt(cls, e_init: Exception, e_unregister: Exception):
        ensure_hasattr: Callable[[str], None]
        ensure_hasattr = lambda name: raise_if(
            not hasattr(cls, name),
            NoAttrError(cls, name),
        )

        cls_setattr: Callable[[str, Any], None]
        cls_setattr = lambda name, value: call_chain(
            lambda: ensure_hasattr(name), lambda: setattr(cls, name, value)
        )()

        try:
            cls_setattr("_instance", None)
            cls_setattr("__singleton_initialized__", False)
        except Exception as e:
            # TODO raise exception group, when they will be introduced to Python
            # add e_init then
            raise CriticalUnregisterError(cls, errors=(e_init, e_unregister)) from e


# ******************************************************************************
# * Decorators
# ******************************************************************************

_EnsIniSingT = TypeVar("_EnsIniSingT", bound=type[EnsureInitSingleton])
_ExpIniSingClsT = TypeVar("_ExpIniSingClsT", bound=type[ExplicitReinitSingleton])


@ensure_subcls_on_arg(ExplicitReinitSingleton)
def no_invalidation_error(cls: _ExpIniSingClsT) -> _ExpIniSingClsT:
    """
    Disables raising InvalidationError, instance validity can still be checked
    with a method.
    """

    cls.__singleton_no_raise_invalidation__ = True
    return cls


@ensure_subcls_on_arg(EnsureInitSingleton)
def no_ensure_init(cls: _EnsIniSingT) -> _EnsIniSingT:
    """
    Disables automatic `EnsureInitSingleton`'s or its subclass' `__init__`
    invocation (it is called even if there is no `super` call inside subclass'
    `__init__`).
    """

    cls.__singleton_ensure_init__ = False
    return cls


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
        """
        Unwraps `self` and returns underlying singleton's attribute.
        """

        self._ensure_source_valid()
        return self._wrapped

    @abstractmethod
    def forward_ref(
        self, x: _ToForwardT
    ) -> "AbstractSingletonInstanceFieldRef[_SourceT, _ToForwardT]":
        ...

    def is_source_valid(self, _: _SourceT | None = None) -> TypeGuard[_SourceT]:
        return self._maybe_get_source() is not None

    def __copy__(self) -> Self:
        return type(self)(self._get_source(), self._wrapped)

    @abstractmethod
    def _maybe_get_source(self) -> _SourceT | None:
        ...

    def _get_source(self) -> _SourceT:
        if (source := self._maybe_get_source()) is None:
            raise InvalidationError(self._source_t)
        else:
            return source

    def _forward_ref_as(self, refcls: type[_RefT], x) -> _RefT:
        return refcls(self._get_source(), x)

    def _ensure_source_valid(
        self, source: _SourceT | None = None
    ) -> TypeGuard[_SourceT]:
        """
        Raises InvalidationError if the instance is not valid anymore.
        """

        if not self.is_source_valid(source):
            raise InvalidationError(self._source_t)

        return True


@final
@dataclass(frozen=True)
class SingletonInstanceFieldRef(
    AbstractSingletonInstanceFieldRef, Generic[_SourceT, T]
):
    """
    Adds invalidation on `Singleton` instance field access on shallow level.
    You can wrap nested values by using `forward_ref` method.
    This is NOT a weakref.ReferenceType!
    """

    # This attribute exists only at init and during forwarding the reference
    _source: _SourceT
    _wrapped: T
    _source_t: type[_SourceT] = field(init=False)

    def as_weak(self) -> "SingletonInstanceFieldRefWeak[_SourceT, T]":
        return SingletonInstanceFieldRefWeak(self._source, self._wrapped)

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


@final
@dataclass(frozen=True)
class SingletonInstanceFieldRefWeak(
    AbstractSingletonInstanceFieldRef, Generic[_SourceT, T]
):
    _source: _SourceT
    _wrapped: T
    _source_ref: ReferenceType[_SourceT] = field(init=False)

    _source_t: type[_SourceT] = field(init=False)

    def as_strong(self) -> SingletonInstanceFieldRef[_SourceT, T]:
        return SingletonInstanceFieldRef(self._get_source(), self._wrapped)

    def forward_ref(
        self, x: _ToForwardT
    ) -> "SingletonInstanceFieldRefWeak[_SourceT, _ToForwardT]":
        # we temporarily set a hard reference to the source, if possible
        return self._forward_ref_as(SingletonInstanceFieldRefWeak, x)

    def _maybe_get_source(self) -> _SourceT | None:
        assert isinstance(self._source_ref, ReferenceType)
        return self._source()

    def __post_init__(self) -> None:
        instance = self._source
        cls = type(instance)

        # this dataclass is frozen, hence we must use object.__setattr__
        self_delattr = lambda name: object.__delattr__(self, name)
        self_setattr = lambda name, val: object.__setattr__(self, name, val)
        set_source_t = lambda: self_setattr("_source_t", cls)

        # deleting the hard reference to the source
        with at_exit(lambda: self_delattr("_source")):
            self_setattr("_source_ref", ref(instance))
            set_source_t()
