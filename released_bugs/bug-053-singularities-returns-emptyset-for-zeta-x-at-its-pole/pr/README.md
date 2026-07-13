# Fix singularities(zeta(x)) missing the pole at x = 1

## Summary

`singularities(zeta(x), x, S.Complexes)` currently returns `EmptySet`, even though `zeta(x)` has a simple pole at `x = 1`.

## Reproducer

```python
from sympy import S, limit, symbols, zeta
from sympy.calculus.singularities import singularities

x = symbols("x")
print(singularities(zeta(x), x, S.Complexes))
print(zeta(1))
print(limit(zeta(x), x, 1))
```

Current output:

```text
EmptySet
zoo
zoo
```

## Expected behavior

The returned set should contain `1`.

## Evidence

The Riemann zeta function has a simple pole at `s = 1`; SymPy already knows this through `zeta(1) = zoo` and `limit(zeta(x), x, 1) = zoo`.

## Suggested regression test

`pr/tests/test_bug_053_singularities_returns_emptyset_for_zeta_x_although_x_1_is_a.py` adds a parametrized test for `zeta(x + a)` shifts and checks that each shifted pole is included.
