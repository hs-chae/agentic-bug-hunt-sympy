---
diagnosis_status: located
confidence: 88
location: sympy/calculus/util.py:260
---

## Candidate Summary

`function_range(sqrt(x**2), x, S.Reals)` returns `EmptySet`. Over the reals, `sqrt(x**2) = Abs(x)`, so the range should be `Interval(0, oo)`.

## Call Path

The public call enters `sympy/calculus/util.py::function_range`. It computes `continuous_domain(sqrt(x**2), x, S.Reals)` at line 233, which returns `Interval(-oo, oo)`. It then iterates over that interval at lines 242-281.

For the interval endpoints, lines 253-256 add the two open-end limits. Both `limit(sqrt(x**2), x, -oo, '+')` and `limit(..., oo, '-')` are `oo`. It then computes critical points with `solveset(f.diff(x), x, interval)` at line 260. Here `f.diff(x)` is `sqrt(x**2)/x` (effectively `Abs(x)/x` on reals), and `solveset` returns `EmptySet`.

## Root Cause

The responsible logic is `sympy/calculus/util.py::function_range`, especially lines 253-281. The function only samples interval endpoints and points where `f.diff(symbol) == 0`. It does not also sample points where the derivative is undefined but the original function is continuous.

For `sqrt(x**2)`, the global minimum occurs at the cusp `x = 0`. The derivative expression is undefined there rather than zero, so line 260 finds no critical point. Since the only sampled values are the two infinite endpoint limits, line 281 constructs an interval from `vals.inf == oo` to `vals.sup == oo`, which evaluates to `EmptySet`.

## Mechanism

The range algorithm assumes that extrema inside a continuous interval are found by solving `f' = 0`. That misses nondifferentiable extrema. For `sqrt(x**2)`, the value `0` at `x = 0` is the lower endpoint of the true range, but `0` is absent from `vals`. With `vals` containing only `oo`, the final `Interval(vals.inf, vals.sup, left_open, right_open)` has no finite lower bound and collapses to `EmptySet`, excluding all actual values.

## Suggested Fix Direction

When computing ranges on continuous intervals, include singularities/discontinuities of the derivative that lie inside the original function's continuous domain as candidate points. For this case, solving for where the denominator of `sqrt(x**2)/x` vanishes would add `x = 0`, giving the sampled value `0` and range `Interval(0, oo)`.

## Confidence and Caveats

Confidence is high for the failing mechanism and source location. The broader fix needs care because derivative singularities can be introduced by simplification or may occur outside the original function domain; they should be intersected with `continuous_domain(f, symbol, domain)`.
