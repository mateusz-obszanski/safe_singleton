from abc import ABC
from collections.abc import Hashable
from dataclasses import dataclass, field

from ..exceptions import PrettyError


class RegistryError(PrettyError, ABC):
    """
    Abstract registry error.
    """


@dataclass
class RegistryKeyError(RegistryError, ABC):
    msg: str = field(init=False)
    key: Hashable

    def __post_init__(self) -> None:
        self.msg = repr(self.key)


class AlreadyRegisteredError(RegistryKeyError):
    """
    Raised, when the item is already registered and current registration attempt
    is done without `force=True`.
    """


class NotRegisteredError(RegistryKeyError):
    """
    Raised on unregistration attempt, when given key is not registered.
    """
