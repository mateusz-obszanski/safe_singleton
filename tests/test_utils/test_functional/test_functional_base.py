import pytest

from safe_singleton.utils.functional import (
    call,
    call_on,
    composed,
    lazy_call,
    lazy_call_on,
)

str_append_factory = lambda x: lambda y: f"{y}{x}"

append_b = str_append_factory("b")
append_c = str_append_factory("c")
append_d = str_append_factory("d")

parametrize = pytest.mark.parametrize


CALL_NAMES = ["f", "args", "kwds", "expected"]
CALL_ARGS = [(append_b, ["a"], {}, "ab")]
call_parametrize = lambda f: parametrize(CALL_NAMES, CALL_ARGS)(f)


@call_parametrize
def test_call(f, args, kwds, expected):
    assert call(f, *args, **kwds) == expected


@call_parametrize
def test_call_on(f, args, kwds, expected):
    del kwds
    assert call_on(args[0], f) == expected


@call_parametrize
def test_lazy_call(f, args, kwds, expected):
    assert lazy_call(f, *args, **kwds)() == expected


@call_parametrize
def test_lazy_call_on(f, args, kwds, expected):
    del kwds
    assert lazy_call_on(args[0], f)() == expected


@parametrize(
    ["f1", "f2", "args", "kwds", "expected"], [(append_b, append_c, ["a"], {}, "abc")]
)
def test_composed_two(f1, f2, args, kwds, expected):
    assert composed(f1, f2)(*args, **kwds) == expected


@parametrize(
    ["f1", "f2", "f3", "args", "kwds", "expected"],
    [(append_b, append_c, append_d, ["a"], {}, "abcd")],
)
def test_composed_three(f1, f2, f3, args, kwds, expected):
    assert composed(f1, f2, f3)(*args, **kwds) == expected
