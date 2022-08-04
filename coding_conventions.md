# Coding conventions

## General

- `kwargs` should be named `kwds` (same lenght as `args`)

## Tests

- All tests must be in a separate `tests` directory,
- `tests` directory must be at the same level as a package's directory for
  it to be tested as if it would be imported in a real project,
- `tests` directory must have the same structure as the project. `_base.py`
  files' equivalents must be named `test_<parent-dir>_base.py`.
