# TODOs

- [] AbstractSingletonInstanceFieldRef - \_source attribute is init-only for
  weakref version, but in ABC it is specified normally and in weakref version it
  is simply deleted. This is somewhat ugly. But it works and the field is
  supposed to be private, so whatever?
- [] invalidation
  - [x] getattr - attribute wrapper-getter factory that checks parent instance
        validity,
  - [] maybe option/decorator/class (opt-in/out?) that automatically injects
    above behaviour into instance's fields' and (optional?) nested fields (depth?)
- [] tests with pytest
  - [] coverage with its configuration
  - [] full coverage
  - [] commit hooks
  - [] GitHub hooks
  - [] tests that depend on other's status (plugin)
  - [] test dataclasses (if it will be somehow fixed)
- [] README.md, documentation
- [] deploy to pypi
- [] experimental
  - [] `singleton` and `weak_singleton` decorators that take a class and make it
    a singleton class by using a metaclass that inserts some singleton class
    (with a default value for this class) into its mro (at the end, before the
    `type`?)
