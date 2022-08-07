from abc import ABC

from ..exceptions import CalledNonInitCallableError


class NonInitCallable(ABC):
    """
    Abstract callable class that is not supposed to be initalized, but it is
    a class for some reason e.g. for inheritance from `typing.Generic`.
    """

    def __init__(self, *_, **__) -> None:
        del _, __
        raise CalledNonInitCallableError(self)
