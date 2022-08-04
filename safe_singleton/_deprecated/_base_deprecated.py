"""
Deprecated because metaclasses are problematic to handle and think about. It is
easier and more straightforward to generally use __new__ and classmethods.
"""


from abc import ABC, ABCMeta
from typing import (
    Any,
    ClassVar,
    Generic,
    TypedDict,
    TypeVar,
    cast,
    final,
    overload,
)
from typing_extensions import Self
from uuid import UUID, uuid4
from weakref import ref

from .exceptions import InvalidationError, NoInstanceError, ReinitError


_Self = TypeVar("_Self")


class MetaClassInitDict(TypedDict):
    __module__: str
    __qualname__: str


class SingletonMeta(Generic[_Self], ABCMeta, type):
    def __init__(
        cls: type[_Self], name: str, bases: tuple[type, ...], dct: MetaClassInitDict
    ) -> None:
        del name, bases, dct
        cls._instance: _Self | None = None  # type: ignore

    # @staticmethod
    def __call__(cls, __cls, *args, **kwds) -> _Self:
        """This has a role of `__new__` in `cls`"""

        # cls is passed twice ¯\_(ツ)_/¯
        del __cls

        if not cls.instance_exists():
            return cls._create_and_register_new_instance(*args, **kwds)

        return cast(_Self, cls._instance)

    def instance_exists(cls) -> bool:
        return cls._instance is not None

    @final
    def _create_and_register_new_instance(cls, *args, **kwds) -> _Self:
        instance = cls._create_new_instance(*args, **kwds)
        cls._instance = instance
        return instance

    @final
    def _create_new_instance(cls, *args, **kwds) -> _Self:
        return super().__call__(*args, **kwds)


class NoImplicitReinitSingletonMeta(SingletonMeta, Generic[_Self], ABCMeta):
    def __call__(cls, *args, **kwds) -> _Self:
        if cls.instance_exists():
            raise ReinitError(cls)
        else:
            return super().__call__(cls, *args, **kwds)

    def reinit(cls, *args, **kwds) -> _Self:
        return cls._create_and_register_new_instance(cls, *args, **kwds)


class WeakRefSingletonMeta(NoImplicitReinitSingletonMeta, Generic[_Self], ABCMeta):
    """
    TODO overwrite __call__, instance_exists and _create_and_register_new_instance
    """

    def __init__(cls, *args) -> None:
        super().__init__(*args)
        cls._instance = ref(cls._instance)


class InvalidableSingletonMeta(WeakRefSingletonMeta, Generic[_Self], ABCMeta):
    """
    TODO invalidation of instances - inject current id (or injected
    __singleton_uuid__) checking into __getattribute__.
    """

    _UUID_DUNDER_NAME_INSTANCE: ClassVar[str] = "__singleton_uuid__"

    def __call__(cls, *args, **kwds) -> _Self:
        instance = super().__call__(*args, **kwds)
        new_id = cls.__give_uuid(instance)
        cls.__current_singleton_id__ = new_id

        return instance

    @staticmethod
    def __give_uuid(instance: "Singleton") -> UUID:
        new_id = uuid4()
        setattr(instance, InvalidableSingletonMeta._UUID_DUNDER_NAME_INSTANCE, new_id)
        return new_id

    @staticmethod
    def _get_uuid(instance: "Singleton") -> UUID:
        return getattr(instance, InvalidableSingletonMeta._UUID_DUNDER_NAME_INSTANCE)


class UnsafeSingleton(ABC, metaclass=SingletonMeta):
    """
    Unsafe, because allows for implicit reinitialization.
    Does not work with dataclass - at least dataclass' __init__ is discarded
    """

    @final
    @classmethod
    def get_instance(cls) -> Self:
        if not cls.instance_exists():
            raise NoInstanceError(cls)
        else:
            return cast(Self, cls._instance)

    @final
    @classmethod
    def maybe_get_instance(cls) -> Self | None:
        try:
            return cls.get_instance()
        except NoInstanceError:
            return None


class SimpleSingleton(UnsafeSingleton, ABC, metaclass=NoImplicitReinitSingletonMeta):
    """
    Does not work with dataclass - at least dataclass' __init__ is discarded
    """


class WeakRefSingleton(SimpleSingleton, ABC, metaclass=WeakRefSingletonMeta):
    """
    Holds the instance only as a weak reference - it will vanish, when the last
    variable that referes to that instance disappears.
    """


class Singleton(WeakRefSingleton, ABC, metaclass=InvalidableSingletonMeta):
    """
    Does not work with dataclass - at least dataclass' __init__ is discarded
    """

    def __getattribute__(self, __name: str) -> Any:
        cls = type(self)

        # avoids recursion error, necessary for id check below
        if __name == cls._UUID_DUNDER_NAME_INSTANCE:
            return object.__getattribute__(self, __name)

        ids_do_not_match = cls._get_uuid(self) != cls.__current_singleton_id__

        if not cls.instance_exists() or ids_do_not_match:
            raise InvalidationError(cls)

        return super().__getattribute__(__name)
