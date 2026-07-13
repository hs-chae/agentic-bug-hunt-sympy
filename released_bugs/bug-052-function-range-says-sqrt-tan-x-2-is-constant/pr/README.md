# Fix `function_range` for continuous cusp points

## Summary

`function_range(sqrt(tan(x)**2), x, Interval(-1, 1))` returns `{tan(1)}`, but the expression is `Abs(tan(x))` on the real interval and has range `Interval(0, tan(1))`.

## Reproducer

```python
from sympy import Interval, sqrt, tan, symbols
from sympy.calculus.util import function_range

x = symbols("x")
print(function_range(sqrt(tan(x)**2), x, Interval(-1, 1)))
```

## Expected behavior

The range should include the interior cusp value at `x = 0`, so the result should be `Interval(0, tan(1))`.

## Evidence

On `[-1, 1]`, `tan` is continuous and strictly increasing, so `sqrt(tan(x)**2) = Abs(tan(x))`. Its minimum is `0` at `x = 0`, and its maximum is `tan(1)` at the endpoints.

## Suggested regression test

The included pytest file checks the original interval and five smaller intervals inside `(-pi/2, pi/2)`.
