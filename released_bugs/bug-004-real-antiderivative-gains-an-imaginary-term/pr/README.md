## Title

Fix branch handling for antiderivatives of log(x)/(x**2 - a**2)

## Summary

`integrate(log(x)/(x**2 - 1), x)` returns an antiderivative whose derivative differs from the integrand by a nonzero imaginary branch term at `x = 2`.

## Reproducer

```python
x = symbols("x")
f = log(x)/(x**2 - 1)
F = integrate(f, x)
assert simplify(diff(F, x) - f).subs(x, 2) == 0
```

## Expected Behavior

At regular points away from poles and branch cuts, differentiating the returned indefinite integral should recover the integrand.

## Evidence

The current residual at `x = 2` is numerically `-I*pi/2`.

## Suggested Regression Test

The included parametrized test checks the representative quadratic denominator and five scaled variants.
