from collections.abc import (
    Hashable,
    Iterable,
    ItemsView,
    Iterator,
    KeysView,
    Mapping,
    ValuesView,
)
from contextlib import suppress
from operator import setitem
from typing import Generic, KeysView, Literal, TypeVar, overload

from typing_extensions import Self

from .exceptions import AlreadyRegisteredError, NotRegisteredError

_K = TypeVar("_K", bound=Hashable)
_V = TypeVar("_V")
_T = TypeVar("_T")

_K_other = TypeVar("_K_other", bound=Hashable)
_V_other = TypeVar("_V_other")


class Registry(Mapping, Generic[_K, _V]):
    def __init__(
        self, source: Mapping[_K, _V] | Iterable[tuple[_K, _V]] | None = None
    ) -> None:
        self._memory: dict[_K, _V] = dict(source or {})

    def register(self, key: _K, val: _V, force=False) -> Self:
        remember = lambda: setitem(self._memory, key, val)

        if force:
            remember()
        elif key not in self:
            remember()
        else:
            raise AlreadyRegisteredError(key)

        return self

    def unregister(self, key: _K) -> _V:
        try:
            return self._memory[key]
        except KeyError as e:
            raise NotRegisteredError(key) from e

    def try_register(self, key: _K, val: _V) -> Self:
        with suppress(AlreadyRegisteredError):
            self.register(key, val, force=False)
        return self

    def try_unregister(self, key: _K) -> _V | None:
        try:
            return self.unregister(key)
        except AlreadyRegisteredError:
            return None

    @classmethod
    def from_dict(cls, d: dict[_K, _V]) -> Self:
        return cls._from(d)

    @classmethod
    def from_mapping(cls, m: Mapping[_K, _V]) -> Self:
        return cls._from(m)

    @classmethod
    def from_tuple(cls, t: tuple[tuple[_K, _V], ...]) -> Self:
        return cls._from(t)

    @classmethod
    def from_iterable(cls, i: Iterable) -> Self:
        return cls._from(i)

    @classmethod
    def _from(cls, src) -> Self:
        return cls(dict(src))

    def to_dict(self) -> dict[_K, _V]:
        return dict(self._memory)

    def to_tuple(self) -> tuple[tuple[_K, _V], ...]:
        return tuple(self.items())

    def keys(self) -> KeysView[_K]:
        return self._memory.keys()

    def values(self) -> ValuesView[_V]:
        return self._memory.values()

    def items(self) -> ItemsView[_K, _V]:
        return self._memory.items()

    @overload
    def get(self, k: _K, default: Literal[None] = None, /) -> _V | None:
        ...

    @overload
    def get(self, k: _K, default: _T, /) -> _K | _T:
        ...

    def get(self, k: _K, default: _T | None = None, /) -> _V | _T | None:  # type: ignore
        return self._memory.get(k, default)

    def update(self, other: Mapping[_K, _V] | Iterable[tuple[_K, _V]]) -> Self:
        source: Iterable[tuple[_K, _V]]
        source = other.items() if isinstance(other, Mapping) else other  # type: ignore

        for k, v in source:
            self.register(k, v)

        return self

    def clear(self) -> Self:
        self._memory.clear()
        return self

    def __iter__(self) -> Iterator[_K]:
        return iter(self._memory)

    def __getitem__(self, __k: _K) -> _V:
        return self._memory[__k]

    def __or__(
        self, other: Mapping[_K_other, _V_other]
    ) -> dict[_K | _K_other, _V | _V_other]:
        return self._memory | other

    def __ior__(self, other: Mapping[_K, _V]) -> None:
        self.update(other)

    def __len__(self) -> int:
        return len(self._memory)
