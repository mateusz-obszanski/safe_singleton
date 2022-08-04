from .more import (
    ExplicitReinitSingleton,
    ExplicitReinitWeakRefSingleton,
    abstract_singleton,
)


@abstract_singleton
class Singleton(ExplicitReinitSingleton):
    ...


@abstract_singleton
class WeakRefSingleton(ExplicitReinitWeakRefSingleton):
    ...
