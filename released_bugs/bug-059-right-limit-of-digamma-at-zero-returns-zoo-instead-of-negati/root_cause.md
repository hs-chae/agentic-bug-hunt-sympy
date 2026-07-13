---
diagnosis_status: located
confidence: 86
location: sympy/functions/special/gamma_functions.py:790
---

## Candidate Summary

`limit(polygamma(0, x), x, 0, dir="+")` returns `zoo`, but the right-hand digamma limit is `-oo`.

## Call Path

`limit()` calls `Limit.doit()` in `sympy/series/limits.py`. The meromorphic/lead-term path cannot get a usable leading term for `polygamma(0, x)`, and `gruntz()` also fails while trying to expand `polygamma(0, 1/x)`. `Limit.doit()` then falls back to `heuristics()`, which evaluates the function at the argument limits and constructs `polygamma(0, 0)`.

## Root Cause

The missing local pole expansion is in `sympy/functions/special/gamma_functions.py`, `polygamma._eval_as_leading_term()` around lines 790-798. For `polygamma(0, x)` it computes `n = 0`, `z = x`, does not match its large-argument check, and returns `polygamma(0, x)` unchanged rather than the finite-pole leading term `-1/x`.

That makes `Expr.leadterm()` reject the result because the coefficient still contains `x`. After `gruntz()` raises `PoleError`, `sympy/series/limits.py:83-103` naively applies argument-wise function evaluation, and `polygamma.eval()` at `gamma_functions.py:677-678` turns the pole value `polygamma(0, 0)` into `S.ComplexInfinity`.

## Mechanism

The correct sign lives in the Laurent principal part `polygamma(0, x) = -1/x - EulerGamma + O(x)`. Since `_eval_as_leading_term()` does not expose `-1/x`, the limit machinery never sees a negative coefficient and a `-1` exponent. The fallback only sees the endpoint value and returns the undirected pole marker `zoo`.

## Suggested Fix Direction

Teach `polygamma._eval_as_leading_term()` or a finite-point series method about poles at nonpositive integers. For order `0` at `z = 0`, it should return `-1/z`; more generally it should return the signed principal part at `z = -k` so directional limits can preserve sign.

## Confidence and Caveats

The failing source step is located, and instrumentation showed `leadterm()` and `gruntz()` both fail before `heuristics()` returns `zoo`. I did not produce a patch, and the general polygamma pole formula needs care for all orders and shifted poles.
