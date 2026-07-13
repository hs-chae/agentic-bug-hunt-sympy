# Reject false acot endpoint solutions in solveset

## Summary

`solveset(Eq(acot(x), -pi/2), x, S.Reals)` returns `{0}`, but SymPy's principal `acot(0)` is `pi/2`, so the returned point has residual `pi`.

## Reproducer

```python
from sympy import Eq, S, acot, pi, simplify, solveset, symbols

x = symbols("x")
sol = solveset(Eq(acot(x), -pi/2), x, S.Reals)
print(sol)
print(simplify(acot(0) + pi/2))
print(acot(0))
```

Current output:

```text
{0}
pi
pi/2
```

## Expected behavior

The real solution set should be `EmptySet` for this endpoint, because `-pi/2` is outside SymPy's principal real range for `acot`.

## Suggested regression test

`pr/tests/test_bug_026_solveset_returns_0_for_acot_x_pi_2_although_acot_0_pi_2.py` covers the representative case and five shifted instances.

