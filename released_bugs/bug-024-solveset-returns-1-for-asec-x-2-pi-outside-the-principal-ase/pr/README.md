# Fix solveset returns 1 for asec(x) = 2*pi outside the principal asec range

## Summary

SymPy 1.14.0 currently produces a mathematically incorrect result for `solveset(Eq(asec(x), 2*pi), x, domain=S.Complexes)`.

## Reproducer

Run `reproduce_bug.py` in the artifact bundle. Current output includes:

```text
solution: {1}
residual at returned value: -2*pi
numeric residual: -6.2831853071795864769252867665590057683943387987502
```

## Expected behavior

EmptySet. The principal value asec(1) is 0, and 2*pi is outside the principal inverse-secant value at x = 1.

## Evidence

`related_bugs.py` contains a standalone runner and pytest-compatible parametrized checks for the representative case plus five additional instantiations. On the current version it prints `Incorrect` and exits nonzero.

## Suggested regression test

Add the test in `pr/tests/test_bug_024_*.py` to SymPy's test suite. It is written without artifact-specific path setup.
