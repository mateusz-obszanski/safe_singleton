# Coding conventions

## General

- `kwargs` should be named `kwds` (same lenght as `args`)
- import order:
  - `from __future import ...`,
  - standard modules,
  - standard modules' extensions (e.g. `typing_extensions`, `more_itertools`),
  - nonstandard modules,
  - project's modules, starting from the highest to the lowest (e.g.
    `from .. import ...; from . import ...`)

## Tests

- All tests must be in a separate `tests` directory,
- `tests` directory must be at the same level as a package's directory for
  it to be tested as if it would be imported in a real project,
- `tests` directory must have the same structure as the project. `_base.py`
  files' equivalents must be named `test_<parent-dir>_base.py`,
- callable classes that have no state, are not supposed to store any data and
  are classes only to subclass `Generic` must be named in lower_snake_case.
- typing is a great tool, maybe other users of Your code will want it, use it
  and use it well.
