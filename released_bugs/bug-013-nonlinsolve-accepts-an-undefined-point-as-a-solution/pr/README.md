# Reject denominator-zero solutions in `nonlinsolve`

## Summary

`nonlinsolve` returns a point where the original rational equation is undefined:

```python
from sympy import *

x, y = symbols("x y")
eqs = [(x*y - x)/(x - 1) - y, y - 1]
print(nonlinsolve(eqs, [x, y]))
```

SymPy 1.14.0 returns `{(1, 1)}`, but substituting that point into the original first equation gives `nan` because `x - 1 = 0`.

## Expected Behavior

The solution set should be `EmptySet`. The second equation forces `y = 1`; clearing the rational equation then forces `x = y = 1`, but the clearing step is only valid when `x != 1`.

## Evidence

```python
>>> ((x*y - x)/(x - 1) - y).subs({x: 1, y: 1})
nan
```

The denominator exclusion is known to the solver machinery, but the zero-dimensional polynomial success path returns before applying it.

## Suggested Regression Test

The attached parametrized test checks the representative case and five analogous shifted cases.
