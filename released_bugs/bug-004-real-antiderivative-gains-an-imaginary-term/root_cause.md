---
diagnosis_status: located
confidence: 82
location: sympy/integrals/meijerint.py:196 and sympy/integrals/meijerint.py:1653-1740
---

## Candidate Summary

`integrate(log(x)/(x**2 - 1), x)` returns an antiderivative whose derivative differs from the integrand by `-I*pi/2` at `x = 2`.

## Call Path

The public `integrate` call enters `Integral._eval_integral`. Direct Risch/heurisch paths do not solve the original integrand. `manualintegrate` applies integration by parts:

```text
(log(x - 1)/2 - log(x + 1)/2)*log(x)
  - Integral(log(x - 1)/x, x)/2
  + Integral(log(x + 1)/x, x)/2
```

Because this manual result still contains `Integral`, `Integral._eval_integral` recursively evaluates those subintegrals with other algorithms. `Integral(log(x - 1)/x, x)` is solved by `meijerint_indefinite`.

## Root Cause

The faulty subresult is:

```python
Integral(log(x - 1)/x, x).doit()
```

It is produced by `sympy/integrals/meijerint.py`, `meijerint_indefinite` and `_meijerint_indefinite_1` around lines 1653-1740, after rewriting `log(x - 1)` through the Meijer lookup table entry for `log(t + a)` around line 196.

For `log(x - 1)`, `_rewrite_single` returns a branch-sensitive representation involving `x*exp_polar(-I*pi)` and `I*pi` constants. The resulting antiderivative differentiates at `x = 2` to `log(x - 1)/x + I*pi/x`, not to `log(x - 1)/x`.

## Mechanism

The original integral is reduced by parts to two logarithmic subintegrals. The `log(x + 1)/x` subintegral differentiates correctly. The `log(x - 1)/x` subintegral does not: on the positive side of the branch point, the Meijer/polylog expression behaves like an antiderivative for a different principal-log branch, adding `I*pi/x`.

The original antiderivative includes `-Integral(log(x - 1)/x, x)/2`, so the extra derivative term becomes `-I*pi/(2*x) * x` in the simplified residual at `x = 2`, observed as `-I*pi/2`.

## Suggested Fix Direction

The Meijer rewrite for shifted logarithms should either preserve the principal branch of `log(x - 1)` under the shift/sign rewrite or decline this transformation when the shift crosses the logarithm branch cut. A conservative fix would make `meijerint_indefinite(log(x - 1)/x, x)` return unevaluated unless it can attach correct branch conditions.

## Confidence and Caveats

Confidence is moderately high. The failing subintegral and Meijer path are directly reproducible, and differentiating that subresult shows the exact extra `I*pi/x`. The broader branch machinery in `meijerint.py` is complex, so the exact minimal patch point may involve helper functions below the lookup-table formula rather than only the table entry.
