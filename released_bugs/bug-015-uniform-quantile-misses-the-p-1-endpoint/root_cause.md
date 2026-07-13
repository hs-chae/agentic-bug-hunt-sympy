---
diagnosis_status: located
confidence: 90
location: sympy/stats/crv.py:290
---

## Candidate Summary

`quantile(Uniform("U", 0, 1))(1)` returns `EmptySet`, but the documented quantile definition is an infimum and gives the upper endpoint `1` for `p = 1`.

## Call Path

The public `quantile` function delegates to the random variable's pspace distribution. `SingleContinuousDistribution.quantile` in `sympy/stats/crv.py:296-302` first tries a distribution-specific `_quantile`; `UniformDistribution` does not provide one, so it falls back to `compute_quantile`.

## Root Cause

The faulty generic algorithm is `sympy/stats/crv.py:285-291`, especially:

```python
cdf = integrate(pdf, (x, left_bound, x), **kwargs)
quantile = solveset(cdf - p, x, self.set)
return Lambda(p, Piecewise((quantile, (p >= 0) & (p <= 1)), (nan, True)))
```

It computes quantiles by solving `F(x) = p` over `self.set`. For `Uniform(0, 1)`, tracing `compute_quantile()` produced:

```text
Lambda(_p, Piecewise((Intersection({_p}, Interval.Ropen(0, 1)), (_p >= 0) & (_p <= 1)), (nan, True)))
```

The equality-solving path has converted the inverse CDF to a set intersected with `Interval.Ropen(0, 1)`, excluding the right endpoint before the public call substitutes `p = 1`.

## Mechanism

The mathematical quantile is not just the solution set of `F(x) = p`; it is `inf{x : p <= F(x)}` as documented in `sympy/stats/rv.py:1198-1203`. At `p = 1`, the infimum is the right endpoint. The generic implementation therefore loses endpoint quantiles by representing the inverse as an equality solution set with an open right endpoint.

## Suggested Fix Direction

Implement quantile through the documented inequality/infimum definition, or add endpoint handling after solving `F(x) = p`: if `p == 1`, return the support supremum when the CDF at that endpoint is `1`.

## Confidence and Caveats

High confidence for the generic quantile root cause. A distribution-specific `_quantile` for `UniformDistribution` would also fix this case, but the underlying generic algorithm remains endpoint-fragile.
