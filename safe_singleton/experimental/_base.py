from contextlib import suppress
from dataclasses import dataclass, field
from functools import wraps
from typing import Any, ClassVar, Generic, Protocol, TypeVar

from typing_extensions import Self
from weakref import ReferenceType, ref

from safe_singleton.utils.context import set_del_attr

from ..exceptions import ImplicitReinitError
from ..utils.registry import Registry
from ..utils.registry.exceptions import AlreadyRegisteredError, NotRegisteredError
from .exceptions import (
    GetInstanceError,
    GetInvalidatedInstanceError,
)


_T = TypeVar("_T")
_Cls = TypeVar("_Cls", bound=type)


class RegistryDecorator(Protocol, Generic[_Cls]):
    def __call__(self, cls: _Cls) -> _Cls:
        ...


@dataclass
class SingletonRegistry(Generic[_T]):

    # Unregistration is not a good idea, singletons are not supposed to stop
    # being ones, if it would be via inheritance, there would almost be no way
    # except for messing with metaclasses in a very ugly way.

    _BYPASS_MEMORIZE_DUNDER: ClassVar[str] = "__singleton_bypass_memorize__"

    _memory: Registry[type[_T], _T] = field(default_factory=Registry)

    def get_instance(self, cls: type[_T]) -> _T:
        try:
            return self._recall(cls)
        except NotRegisteredError as e:
            raise GetInstanceError(cls) from e

    def register(self, cls: type[_T]) -> Self:
        self._wrap_init(cls)
        return self

    def _wrap_init(self, cls: type[_T]) -> None:
        original_init = cls.__init__

        @wraps(original_init)
        def __init__(_self: _T, *args, **kwds):
            try:
                # for reinit
                if not self._memorization_bypassed(cls):
                    self._memorize(cls, _self)
                original_init(_self, *args, **kwds)
            except AlreadyRegisteredError as e:
                raise ImplicitReinitError(cls) from e

        setattr(cls, original_init.__name__, original_init)

    def _memorize(self, cls: type[_T], instance: _T) -> None:
        self._memory.register(cls, instance)

    def _recall(self, cls: type[_T]) -> _T:
        return self._memory[cls]

    @classmethod
    def _memorization_bypassed(cls, _cls: type[_T]) -> bool:
        return getattr(_cls, cls._BYPASS_MEMORIZE_DUNDER, False)


@dataclass
class SingletonWeakRegistry(SingletonRegistry, Generic[_T]):
    _memory: Registry[type[_T], ReferenceType[_T]] = field(
        init=False, default_factory=Registry
    )

    def _memorize(self, cls: type[_T], instance: _T) -> None:
        self._memory.register(cls, ref(instance))

    def _recall(self, cls: type[_T]) -> _T:
        instance_ref = self._memory[cls]
        if (instance := instance_ref()) is None:
            # forget about the class if its instance does not exist
            with suppress(NotRegisteredError):
                self._memory.unregister(cls)
            raise GetInvalidatedInstanceError(cls)
        else:
            return instance


__GLOBAL_SINGLETON_REGISTRY = SingletonRegistry()
__GLOBAL_WEAK_SINGLETON_REGISTRY = SingletonWeakRegistry()


def register(
    registry: SingletonRegistry | None = None, *, weak_registry: bool = False
) -> RegistryDecorator:
    registry = _dispatch_registry(registry, weak=weak_registry)

    def register_decorator(cls: _Cls) -> _Cls:
        registry.register(cls)
        return cls

    return register_decorator


def reinit(
    cls: type[_T],
    args: tuple = (),
    kwds: dict[str, Any] | None = None,
    registry: SingletonRegistry | None = None,
    *,
    weak_registry: bool = False,
) -> _T:
    registry = _dispatch_registry(registry, weak=weak_registry)

    with set_del_attr(cls, type(registry)._BYPASS_MEMORIZE_DUNDER, True):
        return cls(*args, **(kwds or {}))


def _dispatch_registry(
    registry: SingletonRegistry | None, weak: bool
) -> SingletonRegistry:
    if registry is not None:
        return registry
    elif weak:
        return __GLOBAL_WEAK_SINGLETON_REGISTRY
    else:
        return __GLOBAL_SINGLETON_REGISTRY
