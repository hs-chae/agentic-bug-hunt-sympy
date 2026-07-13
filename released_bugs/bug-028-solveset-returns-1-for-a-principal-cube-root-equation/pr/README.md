# Fix solveset principal odd-root inversion over the reals

## Summary

`solveset` currently returns negative real solutions for equations involving principal rational powers, for example `x**Rational(1, 3) = -1`. These are solutions of the real-root interpretation, not of SymPy's principal `Pow`.

## Reproducer

```python
from sympy import Eq, Rational, S, solveset, symbols

x = symbols("x")
print(solveset(Eq(x**Rational(1, 3), -1), x, S.Reals))
```

Current output is `{-1}`. Substitution gives `1 + (-1)**(1/3)`, numerically `1.5 + 0.8660254037844386*I`.

## Expected behavior

The real-domain solution set should be `EmptySet` for these principal-power equations.

## Evidence

The attached regression test covers odd denominators `3, 5, 7, 9, 11, 13`. Each returned `-1` is rejected by direct principal-branch numerical evaluation.

## Suggested regression test

Add `test_bug_028_solveset_over_the_reals_returns_1_for_the_principal_cube_roo.py` to the solver tests.
