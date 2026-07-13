# Fix Uniform quantile at p = 1

## Summary

`quantile(Uniform("U", 0, 1))(1)` currently returns `EmptySet`. The documented quantile definition gives the upper endpoint at `p = 1`, so the result should be `{1}` under the existing set-valued quantile API.

## Reproducer

```python
from sympy import S
from sympy.stats import P, Uniform, cdf, quantile

U = Uniform("U", 0, 1)
print(quantile(U)(S.One))
print(cdf(U)(S.One))
print(P(U <= 1))
```

Current output:

```text
EmptySet
1
1
```

## Expected Behavior

For `U ~ Uniform(0, 1)`, `F(x) < 1` for every `x < 1` and `F(1) = 1`, so the documented definition

```text
Q(p) = inf{x : p <= F(x)}
```

gives `Q(1) = 1`. SymPy should return `{1}`.

## Cause

The generic continuous quantile path in `sympy/stats/crv.py` solves `F(x) = p` over the support. For a Uniform distribution this builds an inverse expression intersected with `Interval.Ropen(0, 1)`, which excludes `p = 1` before substitution.

## Suggested Regression Test

The proposed test file is `tests/test_bug_015_uniform_quantile_misses_the_p_1_endpoint.py`. It checks the representative unit interval and five additional finite Uniform intervals.
