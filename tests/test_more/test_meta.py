from safe_singleton.more._meta import SingletonMeta


def test_basic_singleton_definition_with_metaclass():
    class Foo(metaclass=SingletonMeta):
        ...

    Foo()
