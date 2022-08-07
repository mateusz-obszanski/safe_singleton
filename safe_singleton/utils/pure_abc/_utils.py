from abc import ABC
from typing import TypeGuard


def is_pure_abc(cls: type) -> TypeGuard[ABC]:
    return ABC in cls.__bases__
