# Fix branch sign in Meijer indefinite integral for 1/(x*sqrt(x**2 + a))

## Summary

`integrate(1/(x*sqrt(x**2 + 1)), x)` returns `-asinh(1/x)`, whose derivative has the wrong sign for negative real `x`. The Meijer indefinite path loses the sign branch introduced by a substitution through `x**2`.

## Reproducer

```python
from sympy import *
x = symbols("x")
integrand = 1/(x*sqrt(x**2 + 1))
F = integrate(integrand, x)
print(F)
print(N(integrand.subs(x, -2), 50))
print(N(diff(F, x).subs(x, -2), 50))
```

Current output:

```text
-asinh(1/x)
-0.22360679774997896964091736687312762354406183596115
0.22360679774997896964091736687312762354406183596115
```

## Expected behavior

The returned antiderivative should differentiate to the integrand on the negative real branch or carry a branch condition.

## Evidence

The artifact `related_bugs.py` covers six positive constants `a` in `1/(x*sqrt(x**2 + a))` and checks the derivative numerically at `x = -2`.

## Suggested regression test

Add `pr/tests/test_bug_036_integrate_returns_an_antiderivative_with_the_wrong_sign_on_t.py`.
