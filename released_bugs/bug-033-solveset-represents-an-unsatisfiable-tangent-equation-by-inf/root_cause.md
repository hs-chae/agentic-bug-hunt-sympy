---
diagnosis_status: located
confidence: 90
location: sympy/solvers/solveset.py:467
---

## Candidate Summary

`solveset(Eq(tan(x), I), x, domain=S.Complexes)` returns `ImageSet(Lambda(_n, _n*pi + oo*I), Integers)`. The finite complex equation has no solution because it would require `exp(2*I*x) = 0`.

## Call Path

`solveset` rewrites the `Eq` as `tan(x) - I` in `sympy/solvers/solveset.py:_solveset`. `_is_function_class_equation` detects a trigonometric equation and calls `_solve_trig` at `solveset.py:1287`. Because there is exactly one trig atom, `_solve_trig` directly calls `_invert(f, 0, symbol, domain)` at `solveset.py:821`.

`_invert_complex` first moves the additive `-I`, so it inverts `tan(x) = I`. `_invert_trig_hyp_complex` handles tangent at `solveset.py:467-468` with `n*pi + trig.inverse()(a)`. Here `trig.inverse()` is `atan`, and `atan(I)` evaluates to `oo*I` via the pure-imaginary branch in `sympy/functions/elementary/trigonometric.py:2681-2684`.

## Root Cause

The responsible solver code is `sympy/solvers/solveset.py:_invert_trig_hyp_complex`, lines `467-473`. The tangent inverse branch blindly constructs an integer-periodic image set using `atan(a)` for every finite target `a`, without rejecting tangent's singular target values `a = I` and `a = -I` where the inverse is infinite and no finite preimage exists.

## Mechanism

For `a = I`, `atan(I)` evaluates to `oo*I`, reflecting a logarithmic singularity of the inverse tangent. `_invert_trig_hyp_complex` inserts that into `n*pi + atan(I)` and returns `ImageSet(Lambda(_n, _n*pi + oo*I), Integers)`. No later step intersects this with finite complex numbers or treats the infinite inverse as an empty preimage, so `solveset` returns an infinity-valued image set for an equation over `S.Complexes`.

## Suggested Fix Direction

In the tangent/cotangent complex inverse branch, detect targets for which `trig.inverse()(a)` is not finite, especially `tan(x) = I` and `tan(x) = -I`, and return `EmptySet` for those targets. More generally, filter inverse image sets to finite complex values.

## Confidence and Caveats

Confidence is high. A pinned trace showed `invert_complex(tan(x), I, x)` returns `(x, ImageSet(Lambda(_n, _n*pi + oo*I), Integers))`, and `atan(I)` evaluates to `oo*I`.
