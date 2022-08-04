from abc import ABC
from typing import Any, ClassVar, TypeVar, final

from typing_extensions import Self

from ._meta import SingletonMeta
from ..exceptions import (
    AbstractSingletonInitError,
    InvalidationError,
    NoInstanceError,
    ReinitError,
)


_AbstractSingletonCls = TypeVar("_AbstractSingletonCls", bound=SingletonMeta)


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
        if (i := cls._instance) is None:
            raise NoInstanceError(cls)
        else:
            return i

    @classmethod
    def instance_exists(cls) -> bool:
        return cls.get_instance() is not None

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
    referenced attributes of singletons, so use with caution. Each instance can
    check, whether it is valid, by calling `is_instance_valid` method.
    """

    # ? maybe create another clas above that does not raise InvalidationError

    @classmethod
    def reinit(cls, *args, **kwds) -> Self:
        cls._unregister_instance()
        new_instance = cls(*args, **kwds)
        return new_instance

    def is_instance_valid(self) -> bool:
        try:
            return id(self) == id(type(self).get_instance())
        except NoInstanceError:
            return False

    @classmethod
    def invalidate_singleton(cls, raise_invalidation=False) -> None:
        cls._unregister_instance()

        if raise_invalidation:
            raise InvalidationError(cls)

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
