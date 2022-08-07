from ._meta import PureAbcMeta


class PureAbc(metaclass=PureAbcMeta):
    """
    Its subclasses cannot be initialized if `ABC` is one of their immediate
    bases.
    """


class PureAbcException(PureAbc, Exception):
    """
    An abstract exception that cannot be initialized even if it does not contain
    `abstractmethod`s.
    """
