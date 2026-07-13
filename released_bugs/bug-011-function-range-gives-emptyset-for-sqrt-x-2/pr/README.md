# Fix function_range for sqrt(x**2) over the reals

## Summary

`function_range(sqrt(x**2), x, S.Reals)` currently returns `EmptySet`, although the expression is `Abs(x)` on the real line.

## Reproducer

```python
from sympy import *
from sympy.calculus.util import function_range

x = symbols("x")
print(function_range(sqrt(x**2), x, S.Reals))
```

## Expected behavior

The range should be `Interval(0, oo)`.

## Evidence

The expression directly attains `0`, `2`, and `3`, all excluded by `EmptySet`. The artifact `related_bugs.py` checks the direct real formula with Python `math.sqrt`.

## Suggested regression test

Add `pr/tests/test_bug_011_function_range_returns_emptyset_for_sqrt_x_2_over_the_reals.py`, which parametrizes the representative case plus five shifted square-root cusp cases.
