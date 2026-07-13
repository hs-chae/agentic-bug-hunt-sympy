---
diagnosis_status: located
confidence: 86
location: sympy/functions/special/error_functions.py:1226 and sympy/functions/special/error_functions.py:1443
---

## Candidate Summary

`series(expint(2, x), x, 0, 2)` for positive real `x` returns `1 + x*(log(x) - 1 + EulerGamma - I*pi) + O(x**2)`, with a spurious imaginary term.

## Call Path

The public call is `series(expint(2, x), x, 0, 2)`.
`expint._eval_nseries` in `sympy/functions/special/error_functions.py:1437` sees positive integer order `nu > 1` and rewrites through `_eval_rewrite_as_Ei` at lines 1443-1445.
For `nu = 2`, that gives `-x*(-Ei(x*exp_polar(I*pi)) + I*pi) + exp(-x)`.
The series of the `Ei(...)` term is then computed by `Ei._eval_nseries`, which rewrites via `Ei._eval_rewrite_as_Si`.

## Root Cause

`Ei._eval_rewrite_as_Si` at `sympy/functions/special/error_functions.py:1226-1227` uses only `z.is_negative` to decide that it should subtract `I*pi`:

`if z.is_negative: return Shi(z) + Chi(z) - I*pi`

For the polar argument `z = x*exp_polar(I*pi)` with `x` positive, SymPy reports `z.is_negative == True`, even though the polar lift is on the upper sheet and already carries the `+I*pi` logarithmic branch. The branch correction is therefore applied to a polar argument where it should not be.

## Mechanism

The correct local behavior is `Ei(x*exp_polar(I*pi)) = EulerGamma + log(x) + I*pi - x + O(x**2)`. The rewrite path subtracts `I*pi`, so SymPy expands it as `EulerGamma + log(x) - x + O(x**2)`. Substituting that into the recurrence expression for `expint(2, x)` leaves the extra `-I*pi*x` term.

## Suggested Fix Direction

Distinguish ordinary negative arguments from polar negative arguments in `Ei._eval_rewrite_as_Si`. The `-I*pi` correction is appropriate for the principal cut-plane value on ordinary negative reals, but not for `exp_polar(I*pi)` inputs. Alternatively, avoid the Ei rewrite in `expint._eval_nseries` for positive integer order and use a real recurrence/series for positive real `z`.

## Confidence and Caveats

Confidence is high. A trace showed `expint(2, x).rewrite(Ei)` becoming `-x*(-Ei(x*exp_polar(I*pi)) + I*pi) + exp(-x)`, `x*exp_polar(I*pi).is_negative` being `True`, and `Ei(x*exp_polar(I*pi)).series(...)` losing the `I*pi` branch constant.
