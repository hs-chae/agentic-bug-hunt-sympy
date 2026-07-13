# Remove the spurious imaginary term from expint(2, x) positive-origin series

## Summary

For positive real `x`, `series(expint(2, x), x, 0, 2)` currently includes `-I*pi*x`. The function has a real integral representation on the positive real axis, and the first-order term should be real.

## Reproducer

```python
from sympy import expint, series, symbols

x = symbols("x", positive=True)
print(series(expint(2, x), x, 0, 2))
```

Actual result: `1 + x*(log(x) - 1 + EulerGamma - I*pi) + O(x**2)`

Expected result: `1 + x*(log(x) - 1 + EulerGamma) + O(x**2)`

## Evidence

The recurrence `E_2(x) = exp(-x) - x*E_1(x)` with the positive-real expansion of `E_1` gives the expected real term. Numerical evaluation at small positive `x` is real.

## Suggested Regression Test

Add `pr/tests/test_bug_061_series_expint_2_x_x_0_adds_a_spurious_imaginary_term_on_the_.py` or equivalent coverage under the special-function series tests.
