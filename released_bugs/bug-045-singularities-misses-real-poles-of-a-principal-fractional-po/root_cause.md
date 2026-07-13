---
diagnosis_status: located
confidence: 90
location: sympy/solvers/solveset.py:612
---

## Candidate Summary

`singularities(1/((x**2)**Rational(1, 3) - 1), x, S.Reals)` returns `EmptySet`, but the denominator vanishes at `x = -1` and `x = 1`.

## Call Path

`sympy.calculus.singularities.singularities` rewrites the expression and iterates over powers. For the reciprocal power, lines 100-102 call:

```python
solveset((x**2)**(1/3) - 1, x, S.Reals)
```

The public `solveset` wrapper then replaces the unconstrained `x` with a real dummy before solving. That replacement rewrites:

```text
(x**2)**(1/3) - 1 -> Abs(_R)**(2/3) - 1
```

The traced internal result is:

```text
_invert(Abs(_R)**(2/3) - 1, 0, _R, S.Reals) -> (_R, EmptySet)
```

## Root Cause

The immediate wrong step is in `sympy/solvers/solveset.py:_invert_abs`, around lines 612-617. `_invert_real` first inverts `Abs(_R)**(2/3) = 1` by treating the even numerator as producing both targets `{1, -1}` for `Abs(_R)`. It then calls `_invert_abs` with `g_ys = {-1, 1}`.

`_invert_abs` rejects the entire finite target set as soon as any target is negative:

```python
elif not ok:
    return symbol, S.EmptySet
```

That is too strong for a mixed finite target set. `Abs(_R) = -1` is impossible, but `Abs(_R) = 1` is valid and should produce `_R = {-1, 1}`. The function should discard the negative target, not discard all targets.

## Mechanism

`singularities` depends on `solveset` to find zeros of the denominator. Because the real-domain wrapper rewrites `(x**2)**(1/3)` to `Abs(_R)**(2/3)`, the solve becomes an absolute-value inversion problem. The finite target set contains one invalid branch (`-1`) and one valid branch (`1`). `_invert_abs` returns `EmptySet` for the whole set, so `solveset` reports no denominator zeros. `singularities` then has no points to add and returns `EmptySet`.

## Suggested Fix Direction

In `_invert_abs`, filter finite `g_ys` to the nonnegative targets before solving, and return `EmptySet` only if no nonnegative targets remain. For unknown-sign targets, preserve conditions as it already tries to do.

## Confidence and Caveats

Confidence is high. Directly calling `_solveset` without the real-dummy rewrite finds `{-1, 1}`, while the real-dummy path rewrites to `Abs(_R)**(2/3) - 1` and fails in `_invert_abs`.
