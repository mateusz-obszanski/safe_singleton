from abc import ABC

from ..exceptions import SingletonError


class UnregisterError(SingletonError, ABC):
    ...


class GetInstanceError(SingletonError):
    ...


class GetInvalidatedInstanceError(GetInstanceError):
    ...
