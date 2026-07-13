---
diagnosis_status: located
confidence: 92
location: sympy/functions/elementary/trigonometric.py:155
---

## Candidate Summary

`sinh(I*pi + I*(pi - 1))` evaluates to `0`, while the same argument combined as `I*(2*pi - 1)` gives `-I*sin(1)`.

## Call Path

`sinh.eval` in `sympy/functions/elementary/hyperbolic.py:189-208` extracts the imaginary coefficient with `_imaginary_unit_as_coefficient` and returns `I*sin(i_coeff)` (line 208). For this unevaluated split argument, the coefficient is the unevaluated add `(-1 + pi) + pi`. `sin.eval` in `sympy/functions/elementary/trigonometric.py:301-382` then calls `_peeloff_pi` (line 382).

## Root Cause

`_peeloff_pi` in `sympy/functions/elementary/trigonometric.py:154-159` loops over `Add.make_args(arg)` and uses `a.coeff(pi)` to remove rational multiples of `pi`. For the nested add term `-1 + pi`, `a.coeff(pi)` is `1`, so the code adds `1` to `pi_coeff` but does not preserve the non-pi remainder `-1` in `rest_terms`.

That turns `pi + (pi - 1)` into an apparent exact `2*pi` before evaluating `sin`.

## Mechanism

The hyperbolic evaluator reduces the original call to `I*sin(pi + (pi - 1))`. `_peeloff_pi` drops the `-1`, returns rest `0` and multiple `2`, and `sin(2*pi)` becomes `0`. That propagates back as `sinh(...) = I*0 = 0`.

## Suggested Fix Direction

When peeling pi from an Add term, only treat the term as a removable pi multiple if the whole term is a pure rational multiple of `pi`, or subtract `K*pi` and keep any nonzero remainder in `rest_terms`.

## Confidence and Caveats

High confidence. Instrumentation showed `i_coeff` is `(-1 + pi) + pi`; the wrong result appears when `_peeloff_pi` processes the nested `pi - 1` addend.
