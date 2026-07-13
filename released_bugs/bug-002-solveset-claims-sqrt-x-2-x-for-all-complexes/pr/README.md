# Fix solveset radical clearing validation for sqrt square equations

## Summary

`solveset(Eq(sqrt(x**2), x), x, domain=S.Complexes)` returns `Complexes`, but `x = -1` is not a solution. Radical clearing produces a tautology and loses the principal-square-root branch condition.

## Reproducer

```python
from sympy import *
x = symbols("x")
eq = Eq(sqrt(x**2), x)
sol = solveset(eq, x, domain=S.Complexes)
print(sol)
print(simplify(eq.lhs.subs(x, -1) - eq.rhs.subs(x, -1)))
```

Current output:

```text
Complexes
2
```

## Expected behavior

The result must not be all complex numbers; it must preserve or check the principal-root branch condition.

## Evidence

The artifact `related_bugs.py` covers the representative case plus five shifts and validates each counterexample with `cmath.sqrt`.

## Suggested regression test

Add `pr/tests/test_bug_002_solveset_over_complexes_claims_sqrt_x_2_x_holds_for_every_co.py`.
