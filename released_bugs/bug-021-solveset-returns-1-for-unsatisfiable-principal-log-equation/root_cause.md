---
diagnosis_status: located
confidence: 90
location: sympy/solvers/solveset.py:550
---

## Candidate Summary

`solveset(Eq(log(x), 2*pi*I), x, domain=S.Complexes)` returns `{1}`, but SymPy's `log` is the principal logarithm and `log(1) = 0`, so the equation has no solution.

## Call Path

`solveset` rewrites the `Eq` to `log(x) - 2*pi*I` and calls `_solveset(..., _check=True)` in `sympy/solvers/solveset.py`. `_solveset` reaches the generic inversion branch and calls `_invert(..., domain=S.Complexes)`, which dispatches to `_invert_complex`.

For this reproducer:

`_invert_complex(log(x) - 2*pi*I, {0}, x)` first removes the additive constant, then handles `log(x)` via the generic `.inverse()` path and returns `(x, {exp(2*pi*I)})`, which simplifies to `(x, {1})`. `_solveset` then returns the finite set.

## Root Cause

The responsible code is `sympy/solvers/solveset.py`, `_invert_complex`, lines 550-557:

```python
if hasattr(f, 'inverse') and f.inverse() is not None and \
   not isinstance(f, TrigonometricFunction) and \
   not isinstance(f, HyperbolicFunction) and \
   not isinstance(f, exp):
    ...
    return _invert_complex(f.args[0],
                           imageset(Lambda(n, f.inverse()(n)), g_ys), symbol)
```

This treats the function inverse of `log` as globally valid over the complex numbers. It applies `exp` to both sides but does not require the right-hand side to lie in the principal branch range of `log`.

The later `_check=True` filtering in `_solveset` only calls `domain_check`, which checks finiteness/singularity, not whether the candidate satisfies the original equation.

## Mechanism

The equation is transformed as:

`log(x) - 2*pi*I = 0` -> `log(x) = 2*pi*I` -> `x = exp(2*pi*I)` -> `x = 1`.

The missing condition is that `2*pi*I` is outside the principal-log image. Substituting back gives `log(1) - 2*pi*I = -2*pi*I`, but `_solveset` accepts `{1}` because no residual check is performed for this fully inverted finite set.

## Suggested Fix Direction

The complex inverse path for `log` should either add the principal-branch range condition for the right-hand side or return a condition set when that condition cannot be resolved. A defensive finite-candidate residual check after branch-sensitive inversion would also reject this case.

## Confidence and Caveats

High confidence. The traced intermediate result is exactly `_invert_complex(...)= (x, {1})`, and no later code validates the original equation beyond domain finiteness.
