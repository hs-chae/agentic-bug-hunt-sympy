---
diagnosis_status: located
confidence: 90
location: sympy/calculus/util.py:260
---

## Candidate Summary

`function_range(sqrt(tan(x)**2), x, Interval(-1, 1))` returns `{tan(1)}`, but on this real interval the expression is `Abs(tan(x))`, whose range is `Interval(0, tan(1))`.

## Call Path

The public call enters `function_range` in `sympy/calculus/util.py:161`. It computes the continuous domain with `continuous_domain` at line 233, then for the interval branch evaluates endpoints at lines 253-258 and critical points from `solveset(f.diff(symbol), symbol, interval)` at line 260.

## Root Cause

`function_range` only considers interval endpoints and zeros of the derivative. It does not include points where the derivative is undefined while the original function is still continuous.

For `sqrt(tan(x)**2)`, `continuous_domain` returns `Interval(-1, 1)`. The derivative is `(2*tan(x)**2 + 2)*sqrt(tan(x)**2)/(2*tan(x))`, which is undefined at `x = 0`; `solveset(derivative, x, Interval(-1, 1))` returns `EmptySet`. Since `x = 0` is not a singularity of the original expression, it is not made an interval boundary either.

## Mechanism

The endpoint values are both `tan(1)`: `f(-1) = tan(1)` and `f(1) = tan(1)`. Because the derivative-zero set is empty and derivative singularities are ignored, `vals` only contains `tan(1)`. Line 281 constructs `Interval(vals.inf, vals.sup)`, which degenerates to `{tan(1)}`. The interior cusp value `f(0) = 0` is never sampled.

## Suggested Fix Direction

When computing critical values, also include finite points inside the interval where `f.diff(symbol)` is undefined but `f` itself is defined and continuous. For this example, the zero of the derivative denominator `tan(x)` should add `x = 0` as a critical point.

## Confidence and Caveats

Confidence is high. I verified the continuous domain, derivative, derivative solve result, and endpoint/cusp values against the checkout.
