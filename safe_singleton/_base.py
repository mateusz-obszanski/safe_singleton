from . import more


@more.abstract_singleton
class Singleton(more.ExplicitReinitSingleton):
    ...


@more.abstract_singleton
class WeakRefSingleton(more.ExplicitReinitWeakRefSingleton):
    ...
