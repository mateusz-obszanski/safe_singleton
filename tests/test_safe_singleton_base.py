from collections.abc import Callable
from typing import TypeVar

import pytest

from safe_singleton import Singleton, WeakRefSingleton
from safe_singleton.exceptions import AbstractSingletonInitError, ImplicitReinitError


_SingClsT = TypeVar("_SingClsT", bound=type[Singleton])
_SingT = TypeVar("_SingT", bound=Singleton)
SingletonCls = type[Singleton]


for_both = pytest.mark.parametrize("cls", [Singleton, WeakRefSingleton])


def subcls_factory(base: _SingClsT) -> _SingClsT:
    class ChildSingleton(base):  # type: ignore
        ...

    return ChildSingleton


def create_subcls_instance(cls: type[_SingT]) -> _SingT:
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


@for_both
def test_get_instance(cls: SingletonCls):
    instance = create_subcls_instance(cls)
    assert instance is type(instance).get_instance()


@for_both
def test_explicit_reinit(cls: SingletonCls):
    subcls = subcls_factory(cls)
    first = subcls()
    assert (second := subcls.reinit()) is not None
    assert first is not second


# TODO more tests for both
# TODO more tests for WeakRefSingleton
