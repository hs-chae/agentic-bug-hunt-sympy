# Fix solveset principal-asin inverse branch check

## Summary

`solveset(Eq(asin(x), pi), x, domain=S.Complexes)` returns `{0}` even though `asin(0) = 0`. The inverse-function solve path needs to respect the image of principal `asin`.

## Reproducer

```python
from sympy import *
x = symbols("x")
eq = Eq(asin(x), pi)
sol = solveset(eq, x, domain=S.Complexes)
print(sol)
print(simplify(eq.lhs.subs(x, 0) - eq.rhs.subs(x, 0)))
```

Current output:

```text
{0}
-pi
```

## Expected behavior

The solver should not return `0`; the equation is unsatisfiable for principal `asin`.

## Evidence

The artifact `related_bugs.py` covers six multiples of `pi` and compares residuals with Python `cmath.asin`.

## Suggested regression test

Add `pr/tests/test_bug_001_solveset_returns_0_for_asin_x_pi_outside_the_principal_asin_.py`.
