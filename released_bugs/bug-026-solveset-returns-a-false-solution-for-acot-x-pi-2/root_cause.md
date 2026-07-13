---
diagnosis_status: located
confidence: 90
location: sympy/solvers/solveset.py:230
---

## Candidate Summary

`solveset(Eq(acot(x), -pi/2), x, S.Reals)` returns `{0}`, but `acot(0)` is `pi/2`, so the returned point does not satisfy the equation.

## Call Path

`solveset` converts the equation to `acot(x) + pi/2 = 0` and calls `_solveset`. The generic inversion path calls `_invert(acot(x) + pi/2, 0, x, S.Reals)`. `_invert_real` first subtracts `pi/2`, then handles `acot(x)` using the generic inverse-function branch.

## Root Cause

The responsible code is `sympy/solvers/solveset.py`, `_invert_real`, lines 230-238, combined with `acot.inverse()` in `sympy/functions/elementary/trigonometric.py` lines 2992-2996.

`_invert_real` has a generic branch:

```python
if hasattr(f, 'inverse') and f.inverse() is not None and not isinstance(f, (
        TrigonometricFunction,
        HyperbolicFunction,
        )):
    ...
    return _invert_real(f.args[0],
                        imageset(Lambda(n, f.inverse()(n)), g_ys),
                        symbol)
```

For `acot(x) = -pi/2`, this applies `acot.inverse()`, which is `cot`, and turns the target value into `cot(-pi/2) = 0`. There is no range check that `-pi/2` is in the principal real range of `acot`, documented in the `acot` class as `(-pi/2, pi/2]`.

## Mechanism

The inversion sequence is:

1. `acot(x) + pi/2 = 0`
2. `acot(x) = -pi/2`
3. generic inverse branch applies `cot` to the right-hand side
4. `x = cot(-pi/2) = 0`

This is algebraically invalid for the principal branch because `cot` is periodic and not a two-sided inverse of `acot` outside the branch range. SymPy's own `acot.eval` returns `pi/2` at zero, so substituting the returned solution gives residual `pi`, not `0`.

## Suggested Fix Direction

The generic inverse-function branch should not blindly invert inverse trigonometric functions. It should intersect target values with the principal range of the inverse function before applying the inverse, or special-case inverse trig functions with branch-aware range checks. For `acot`, the target must be in `(-pi/2, pi/2]`.

## Confidence and Caveats

Confidence is high: `invert_real(acot(x), -pi/2, x)` directly returns `(x, {0})`, and the source branch that applies `cot` without a range guard is explicit. Other inverse trig functions may have analogous endpoint/range issues.
