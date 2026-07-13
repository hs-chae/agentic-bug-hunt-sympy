# Fix singularities missing polylog(1, z) logarithmic singularities

## Summary

`singularities(polylog(1, x), x, S.Complexes)` returns `EmptySet`, but `polylog(1, x) = -log(1 - x)` and is singular at `x = 1`.

## Reproducer

```python
from sympy import S, polylog, symbols
from sympy.calculus.singularities import singularities

x = symbols("x")
print(singularities(polylog(1, x), x, S.Complexes))
print(polylog(1, x).subs(x, 1))
```

Current output:

```text
EmptySet
zoo
```

## Expected behavior

The singularity set should include `x = 1`.

## Evidence

The artifact `related_bugs.py` checks the identity `polylog(1, z) = -log(1 - z)` with Python `cmath` and covers six linear arguments whose argument reaches `1`.

## Suggested regression test

See `pr/tests/test_bug_055_singularities_misses_the_pole_of_polylog_1_x_at_x_1.py`.
