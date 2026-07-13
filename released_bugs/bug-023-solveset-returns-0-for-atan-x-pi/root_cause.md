---
diagnosis_status: located
confidence: 92
location: sympy/solvers/solveset.py:550
---

## Candidate Summary

`solveset(Eq(atan(x), pi), x, domain=S.Complexes)` returns `{0}`. Direct substitution fails because `atan(0) = 0`, not `pi`.

## Call Path

`solveset` converts the `Eq` to `atan(x) - pi` in `sympy/solvers/solveset.py:_solveset`. This expression is not handled by `_solve_trig`, so `_solveset` reaches the generic inversion call at `solveset.py:1313`. `_invert` dispatches to `_invert_complex`.

The concrete path is:

`atan(x) - pi = 0` -> remove additive `-pi` -> `atan(x) = pi` -> generic inverse-function branch in `_invert_complex` -> `atan(x).inverse()` is `tan` (`sympy/functions/elementary/trigonometric.py:2775`) -> `x = tan(pi)` -> `{0}`.

## Root Cause

The bug is in `sympy/solvers/solveset.py:_invert_complex`, lines `550-557`. That branch applies `f.inverse()` for any one-argument function with an inverse, except ordinary trig/hyperbolic/exp classes. Inverse trigonometric functions are not excluded, so `atan` is inverted by applying `tan` to the right-hand side with no principal-range check.

## Mechanism

For this reproducer, `_invert_complex` maps `{pi}` through `tan`, producing `{0}`. `_solveset` accepts the finite set because `atan(x) - pi` is defined at `x=0`. There is no residual equality check, so the solver returns a point that solves only `tan(atan(x)) = tan(pi)`, not the original principal-value equation.

## Suggested Fix Direction

Handle inverse trigonometric functions as partial inverses: only invert when the target is known to be in the principal range, or post-filter finite candidates against the original equation. `atan` should reject targets such as `pi`.

## Confidence and Caveats

Confidence is high. A pinned trace showed `invert_complex(atan(x) - pi, 0, x)` returns `(x, {0})`, directly matching the observed wrong output.
