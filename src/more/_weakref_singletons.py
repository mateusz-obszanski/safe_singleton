from abc import ABC
from typing import cast

from typing_extensions import Self
from weakref import ref

from src.exceptions import NoInstanceError

from ._base import (
    abstract_singleton,
    SimpleSingleton,
    NoImplicitReinitSingleton,
    ExplicitReinitSingleton,
)


@abstract_singleton
class SimpleWeakRefSingleton(SimpleSingleton, ABC):
    @classmethod
    def _register_new_instance(cls, i: Self) -> Self:
        cls._instance = ref(i)
        # Instance must be returned, because otherwise `cls` will lose the only
        # one hard reference to the instance during it very initialization
        return i


@abstract_singleton
class NoImplicitReinitWeakRefSingleton(
    SimpleWeakRefSingleton, NoImplicitReinitSingleton, ABC
):
    """
    See `NoImplicitReinitSingleton`.
    """

    @classmethod
    def get_instance(cls) -> Self:
        if cls._instance is None or (i := cls._instance()) is None:
            raise NoInstanceError(cls)
        else:
            return cast(Self, i)


@abstract_singleton
class ExplicitReinitWeakRefSingleton(
    NoImplicitReinitWeakRefSingleton, ExplicitReinitSingleton, ABC
):
    ...
