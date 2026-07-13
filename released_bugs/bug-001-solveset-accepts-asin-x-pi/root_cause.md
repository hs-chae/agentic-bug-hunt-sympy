---
diagnosis_status: located
confidence: 88
location: sympy/solvers/solveset.py:550
---

## Candidate Summary

`solveset(Eq(asin(x), pi), x, domain=S.Complexes)` returns `{0}`, but `asin(0) = 0`, not `pi`.

## Call Path

`solveset` converts the equation to `asin(x) - pi = 0` and enters `_solveset`. The expression is not treated by `_solve_trig` because the top-level function is the inverse trigonometric function `asin`, not `sin`. `_solveset` then calls `_invert(..., domain=S.Complexes)`, which dispatches to `_invert_complex`.

For this reproducer, `_invert_complex(asin(x) - pi, {0}, x)` removes the additive constant, then uses the generic `.inverse()` path for `asin`, producing `(x, {sin(pi)}) = (x, {0})`.

## Root Cause

The responsible code is the same generic inverse block in `sympy/solvers/solveset.py`, `_invert_complex`, lines 550-557. It applies `f.inverse()` for any non-trigonometric, non-hyperbolic, non-exp function:

```python
return _invert_complex(f.args[0],
                       imageset(Lambda(n, f.inverse()(n)), g_ys), symbol)
```

For `asin`, this uses `sin` as though `asin` were globally invertible with no range condition. That is false for the principal inverse sine: `asin(z) = y` implies `y` must be in the selected principal branch image.

## Mechanism

The solver transforms:

`asin(x) - pi = 0` -> `asin(x) = pi` -> `x = sin(pi)` -> `x = 0`.

The principal `asin` branch does not take the value `pi`, so `sin(pi)=0` is only a solution to `sin(y)=x`, not to `asin(x)=y`. `_solveset` returns the finite inversion result after only `domain_check`, which does not test the residual `asin(0) - pi`.

## Suggested Fix Direction

Inverse-function handling for principal inverse functions should carry range/image conditions. In this case `asin` inversion should require the right-hand side to be in the principal `asin` range/image, or leave a `ConditionSet`/empty set when a concrete value such as `pi` violates it.

## Confidence and Caveats

High confidence. The trace shows `_invert_complex(...)= (x, {0})`, matching the wrong output exactly. I did not audit every other inverse elementary function using this generic path.
