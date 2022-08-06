"""
Backend of the module. Provides singletons with varying behaviour complexity
and `abstract_singleton` decorator for custom abstract singletons.
"""

from ._base import (
    SimpleSingleton,
    NoImplicitReinitSingleton,
    ExplicitReinitSingleton,
    EnsureInitSingleton,
    abstract_singleton,
)
from ._decorators import abstract_singleton
from ._meta import SingletonMeta
from ._weakref_singletons import (
    SimpleWeakRefSingleton,
    NoImplicitReinitWeakRefSingleton,
    ExplicitReinitWeakRefSingleton,
    EnsureInitWeakRefSingleton,
)
