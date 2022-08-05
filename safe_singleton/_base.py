from .more import (
    ExplicitReinitSingleton,
    ExplicitReinitWeakRefSingleton,
    abstract_singleton,
)


@abstract_singleton
class Singleton(ExplicitReinitSingleton):
    # TODO documentation
    ...


@abstract_singleton
class WeakRefSingleton(ExplicitReinitWeakRefSingleton):
    # TODO documentation
    ...
