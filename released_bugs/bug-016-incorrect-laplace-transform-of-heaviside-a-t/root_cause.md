---
diagnosis_status: located
confidence: 86
location: sympy/integrals/laplace.py:351
---

## Candidate Summary

`laplace_transform(Heaviside(a - t), t, s, noconds=True)` returns `exp(-a*s)/s`. Substituting `a = 2` gives `exp(-2*s)/s`, but the transform of `Heaviside(2 - t)` over `t >= 0` is `(1 - exp(-2*s))/s`.

## Call Path

`laplace_transform` calls `LaplaceTransform(...).doit`, which calls `_laplace_transform` at `sympy/integrals/laplace.py:1315`. `_laplace_transform` attempts simple table rules before programmatic Heaviside handling at `sympy/integrals/laplace.py:1236-1241`.

## Root Cause

The simple rule table in `sympy/integrals/laplace.py:351-354` contains both relevant Heaviside patterns:

```python
(Heaviside(a*t-b), exp(-s*b/a)/s, And(a > 0, b > 0), ...)
(Heaviside(a*t-b), (1-exp(-s*b/a))/s, And(a < 0, b < 0), ...)
```

For `Heaviside(a - t)`, the pattern `a*t - b` matches with coefficient `-1` and `b = -a`. The correct rule is the second one, but `_laplace_apply_simple_rules` only applies a rule when its condition is exactly `S.true` (`sympy/integrals/laplace.py:1033-1042`). With symbolic `a`, neither condition is true, so the simple rules fail and the later integration/rule path returns a transform with contradictory condition `(a > 0) & (a < 0) & Ne(1/a, 0)`.

`LaplaceTransform.doit` drops those conditions when `noconds=True` at `sympy/integrals/laplace.py:1317-1318`.

## Mechanism

The returned tuple for the reproducer is `(exp(-a*s)/s, 0, (a > 0) & (a < 0) & Ne(1/a, 0))`. That formula corresponds to a step opening at `t = a`, not a window closing at `t = a`. Because `noconds=True` returns only `r[0]`, the contradictory condition is discarded and the invalid expression becomes the public result. Substituting `a = 2` then preserves the wrong branch.

## Suggested Fix Direction

For symbolic `Heaviside(a - t)`, return a guarded `Piecewise`/conditional transform distinguishing `a > 0` and `a < 0`, or avoid returning a formula whose condition is contradictory when `noconds=True` can discard it. The programmatic `_laplace_rule_heaviside` branch at `sympy/integrals/laplace.py:586-594` already encodes the positive-window logic but only fires when `a.is_positive` or `a.is_negative` is known.

## Confidence and Caveats

High confidence for the bad condition-dropping mechanism. The precise upstream rule that produces the contradictory tuple is in the transform fallback after simple-rule rejection, but the public wrong result depends on `noconds=True` discarding that invalid condition.
