# TODOs

- [] AbstractSingletonInstanceFieldRef - do not use dataclasses for the children,
  simplify the relationships, fix type issues,
- [] invalidation
  - [] getattr - attribute wrapper-getter factory that checks parent instance
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
