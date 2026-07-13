---
diagnosis_status: located
confidence: 92
location: sympy/solvers/solveset.py:550
---

## Candidate Summary

`solveset(Eq(acos(x), 2*pi), x, domain=S.Complexes)` returns `{1}`. Direct substitution fails because `acos(1) = 0`, not `2*pi`.

## Call Path

`solveset(Eq(acos(x), 2*pi), x, S.Complexes)` normalizes the equation to `acos(x) - 2*pi` in `sympy/solvers/solveset.py:_solveset`. Because this is not classified as a `TrigonometricFunction` equation, `_solveset` takes the generic inversion path at `solveset.py:1313`: `lhs, rhs_s = inverter(f, 0, symbol)`. That calls `_invert(..., domain=S.Complexes)`, then `_invert_complex`.

The concrete inversion trace is:

`acos(x) - 2*pi = 0` -> `_invert_complex` removes the additive `-2*pi` -> `acos(x) = 2*pi` -> generic inverse-function branch calls `acos(x).inverse()`, which is `cos` (`sympy/functions/elementary/trigonometric.py:2560`) -> `x = cos(2*pi)` -> `{1}`.

## Root Cause

The responsible code is `sympy/solvers/solveset.py:_invert_complex`, especially the generic inverse branch at lines `550-557`:

```python
if hasattr(f, 'inverse') and f.inverse() is not None and \
   not isinstance(f, TrigonometricFunction) and \
   not isinstance(f, HyperbolicFunction) and \
   not isinstance(f, exp):
    ...
    return _invert_complex(f.args[0],
                           imageset(Lambda(n, f.inverse()(n)), g_ys), symbol)
```

For inverse trigonometric functions such as `acos`, this treats `cos` as a globally valid inverse and does not attach any condition that the right-hand side lies in the principal range of `acos`.

## Mechanism

With `g_ys = {2*pi}`, line `557` constructs `imageset(Lambda(n, cos(n)), {2*pi})`, which evaluates to `{1}`. `_solveset` then accepts the finite set after only `domain_check`; `domain_check(acos(x) - 2*pi, x, 1)` only verifies that the expression is defined at `x=1`, not that it is zero. The false solution therefore survives even though `acos(1) - 2*pi = -2*pi`.

## Suggested Fix Direction

The generic inverse branch should not be used unconditionally for principal inverse functions. Either exclude inverse trig/hyperbolic functions from this branch and handle them with range-aware logic, or intersect/filter the inverted set by checking the original equation for finite candidate values.

## Confidence and Caveats

Confidence is high because a checkout-pinned trace showed `invert_complex(acos(x) - 2*pi, 0, x)` returns `(x, {1})`, and the cited branch is the step that creates `cos(2*pi)`.
