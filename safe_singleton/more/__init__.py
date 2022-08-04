"""
Backend of the module. Provides singletons with varying behaviour complexity
and `abstract_singleton` decorator for custom abstract singletons.
"""

from ._meta import SingletonMeta
from ._base import (
    SimpleSingleton,
    NoImplicitReinitSingleton,
    ExplicitReinitSingleton,
    abstract_singleton,
)
from ._weakref_singletons import (
    SimpleWeakRefSingleton,
    NoImplicitReinitWeakRefSingleton,
    ExplicitReinitWeakRefSingleton,
)
