# Fix Rayleigh CDF below its support

## Summary

`sympy.stats.cdf` for `Rayleigh` currently returns the closed-form expression
`1 - exp(-z**2/(2*sigma**2))` even when `z < 0`. The Rayleigh distribution has
support `[0, oo)`, so the CDF must be `0` for all negative arguments.

## Reproducer

```python
from sympy.stats import Rayleigh, cdf, P

R = Rayleigh("R", 1)
print(cdf(R)(-1))
print(P(R <= -1))
```

Current output:

```text
1 - exp(-1/2)
0
```

## Expected Behavior

`cdf(R)(-1)` should return `0`. More generally, `cdf(Rayleigh("R", sigma))(z)`
should return `0` for every positive `sigma` and every `z < 0`.

## Evidence

The Rayleigh PDF is supported on `[0, oo)`. Therefore
`F(z) = P(R <= z) = integral_{[0, oo) cap (-oo, z]} f(x) dx = 0` whenever
`z < 0`. SymPy's own probability query `P(R <= -1)` returns `0`, contradicting
the direct CDF call.

## Suggested Regression Test

The proposed test is in
`pr/tests/test_bug_014_rayleigh_cdf_is_positive_below_support.py`. It checks the
representative case plus five additional negative-support instantiations.
