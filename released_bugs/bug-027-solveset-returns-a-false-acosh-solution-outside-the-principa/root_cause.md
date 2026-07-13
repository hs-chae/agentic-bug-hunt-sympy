---
diagnosis_status: located
confidence: 92
location: sympy/solvers/solveset.py:550
---

## Candidate Summary

`solveset(Eq(acosh(x), 2*pi*I), x, domain=S.Complexes)` returns `{1}`. The returned point is false because `acosh(1) = 0`.

## Call Path

`solveset` rewrites the equation as `acosh(x) - 2*pi*I` and reaches the generic inversion path in `sympy/solvers/solveset.py:_solveset` at line `1313`. `_invert` dispatches to `_invert_complex`.

The concrete path is:

`acosh(x) - 2*pi*I = 0` -> remove additive `-2*pi*I` -> `acosh(x) = 2*pi*I` -> `_invert_complex` generic inverse branch -> `acosh(x).inverse()` is `cosh` (`sympy/functions/elementary/hyperbolic.py:1555`) -> `x = cosh(2*pi*I)` -> `{1}`.

## Root Cause

The responsible code is `sympy/solvers/solveset.py:_invert_complex`, lines `550-557`. It treats functions with an `inverse()` method as if that inverse were globally valid. For `acosh`, `cosh` is only an inverse on the principal branch/range, and the branch does not check that `2*pi*I` is in that range.

## Mechanism

Line `557` maps the target set `{2*pi*I}` through `cosh`, giving `{1}`. `_solveset` returns that finite set after a definedness check. Since `acosh(1)` evaluates to `0`, the returned point has residual `-2*pi*I`; the solver has solved the periodic equation `cosh(acosh(x)) = cosh(2*pi*I)` rather than the original principal `acosh` equation.

## Suggested Fix Direction

Exclude inverse hyperbolic functions from the generic inverse branch or add branch-range conditions for their target values. For finite candidates, an equation residual check would also prevent this false solution.

## Confidence and Caveats

Confidence is high. The trace showed `invert_complex(acosh(x) - 2*pi*I, 0, x)` returns `(x, {1})`, and the only step that creates `{1}` is the cited generic inverse mapping through `cosh`.
