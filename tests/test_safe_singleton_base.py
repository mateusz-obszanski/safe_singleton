from collections.abc import Callable
from typing import TypeVar

import pytest

from safe_singleton import Singleton, WeakRefSingleton
from safe_singleton.exceptions import AbstractSingletonInitError, ImplicitReinitError


_SingT = TypeVar("_SingT", bound=type[Singleton])
SingletonCls = type[Singleton]


for_both = pytest.mark.parametrize("cls", [Singleton, WeakRefSingleton])


def subcls_factory(base: _SingT) -> _SingT:
    class ChildSingleton(base):  # type: ignore
        ...

    return ChildSingleton


def create_subcls_instance(cls: _SingT) -> _SingT:
    subcls = subcls_factory(cls)
    return subcls()


@for_both
def test_raises_on_abstract_singleton_init(cls: SingletonCls):
    with pytest.raises(AbstractSingletonInitError):
        cls()


@for_both
def test_init(cls: SingletonCls):
    create_subcls_instance(cls)


@for_both
def test_raises_on_implicit_reinit(cls: SingletonCls):
    subcls = subcls_factory(cls)
    first = subcls()

    with pytest.raises(ImplicitReinitError):
        second = subcls()
        del second

    del first


# TODO more tests for both
# TODO more tests for WeakRefSingleton
