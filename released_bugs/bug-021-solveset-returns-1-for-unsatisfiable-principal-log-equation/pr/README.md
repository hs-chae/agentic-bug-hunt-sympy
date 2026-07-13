# Fix solveset principal-log inverse branch check

## Summary

`solveset(Eq(log(x), 2*pi*I), x, domain=S.Complexes)` returns `{1}`, but `log(1)` is `0` on SymPy's principal logarithm branch. The solver should reject targets outside the principal `log` image or keep the necessary condition.

## Reproducer

```python
from sympy import *
x = symbols("x")
eq = Eq(log(x), 2*pi*I)
sol = solveset(eq, x, domain=S.Complexes)
print(sol)
print(simplify(eq.lhs.subs(x, 1) - eq.rhs.subs(x, 1)))
```

Current output:

```text
{1}
-2*I*pi
```

## Expected behavior

The equation should not return `{1}`; the concrete target `2*pi*I` is outside the principal logarithm range.

## Evidence

The artifact `related_bugs.py` covers six nonzero multiples of `2*pi*I` and compares the residual with Python `cmath.log`.

## Suggested regression test

Add `pr/tests/test_bug_021_solveset_returns_1_for_unsatisfiable_principal_log_equation.py`.
