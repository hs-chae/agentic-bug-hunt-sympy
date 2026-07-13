# Fix limit of derivative of `besselj(1, x)/x` at zero

## Summary

`limit(diff(besselj(1, x)/x, x), x, 0)` currently returns `-oo`, but the
limit is `0`. The same failure appears for several scaled arguments
`besselj(1, c*x)/x`.

## Reproducer

```python
from sympy import besselj, diff, limit, series, symbols

x = symbols("x")
expr = diff(besselj(1, x) / x, x)
print(limit(expr, x, 0))
print(series(expr, x, 0, 5))
```

Current output:

```text
-oo
-x/8 + x**3/96 + O(x**5)
```

## Expected behavior

The limit should be `0`. Since
`besselj(1, x) = x/2 - x**3/16 + O(x**5)`, the quotient is
`besselj(1, x)/x = 1/2 - x**2/16 + O(x**4)`, and its derivative is
`-x/8 + O(x**3)`.

## Evidence

The artifact's `related_bugs.py` checks the representative case and
five scaled cases against an mpmath numerical oracle near zero. On SymPy 1.14.0,
all included cases report an infinite symbolic limit even though the numerical
values are small and tend to zero.

## Suggested regression test

Add `pr/tests/test_bug_039_limit_of_derivative_of_besselj_1_x_x_is_oo_instead_of_0.py`.
