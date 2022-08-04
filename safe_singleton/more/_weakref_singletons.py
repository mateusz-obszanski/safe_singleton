from abc import ABC
from weakref import ReferenceType, ref

from typing_extensions import Self

from ._base import (
    abstract_singleton,
    SimpleSingleton,
    NoImplicitReinitSingleton,
    ExplicitReinitSingleton,
)


@abstract_singleton
class SimpleWeakRefSingleton(SimpleSingleton, ABC):
    def as_ref(self) -> ReferenceType[Self]:
        return ref(self)

    @classmethod
    def get_instance_as_ref(cls) -> ReferenceType[Self]:
        return super().get_instance().as_ref()

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
    def maybe_get_instance(cls) -> Self | None:
        if (instance_ref := cls._instance) is None:
            return None
        else:
            return instance_ref()


@abstract_singleton
class ExplicitReinitWeakRefSingleton(
    NoImplicitReinitWeakRefSingleton, ExplicitReinitSingleton, ABC
):
    ...
