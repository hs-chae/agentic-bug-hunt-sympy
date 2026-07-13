---
diagnosis_status: located
confidence: 93
location: sympy/solvers/solveset.py:230
---

## Candidate Summary

`solveset(Eq(atan2(x, 1), pi), x, S.Reals)` returns `{0}`. Substitution gives `atan2(0, 1) = 0`, so the returned point is not a solution.

## Call Path

`solveset` first replaces the unconstrained user symbol with a real dummy for a real-domain solve at `sympy/solvers/solveset.py:2486-2494`.

With that real dummy, `atan2(_R, 1)` evaluates to `atan(_R)` through `atan2.eval` in `sympy/functions/elementary/trigonometric.py:3715-3717`, since the second argument is positive.

The equation becomes `atan(_R) - pi = 0`. `_solveset` reaches the generic inverter. `_invert_real` removes the additive constant, then uses the generic inverse-function branch at `sympy/solvers/solveset.py:230-238`. Since `atan.inverse()` is `tan`, it maps the right-hand side `pi` to `tan(pi) = 0`.

The final `_check` only calls `domain_check` for finiteness/definedness at `sympy/solvers/solveset.py:1395-1399`; it does not verify that the residual is zero, so `{0}` survives.

## Root Cause

`_invert_real` treats inverse functions such as `atan` as globally invertible onto all real right-hand sides:

```python
imageset(Lambda(n, f.inverse()(n)), g_ys)
```

There is no range guard for `atan`. The valid real range of `atan` is `(-pi/2, pi/2)`, so the right-hand side `pi` should be rejected before applying `tan`.

## Mechanism

The solver converts `atan2(x, 1) = pi` to `atan(x) = pi`. Then it applies `tan` to both sides and obtains `x = tan(pi) = 0`.

This inversion is not reversible because `pi` is outside the principal range of `atan`. The branch/range condition is dropped, so a residual-check failure becomes a reported solution.

## Suggested Fix Direction

When `_invert_real` uses an inverse trigonometric function's `.inverse()`, it should intersect the right-hand side set with that inverse function's actual range. For `atan`, reject values outside `(-pi/2, pi/2)`. A stronger finite-solution residual check would also catch this class of errors.

## Confidence and Caveats

Confidence is high. The `atan2` simplification for positive second argument is mathematically valid; the bug is the subsequent unguarded inversion of `atan`.
