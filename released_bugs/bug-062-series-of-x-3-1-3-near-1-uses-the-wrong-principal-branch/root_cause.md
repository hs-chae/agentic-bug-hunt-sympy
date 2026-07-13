---
diagnosis_status: located
confidence: 96
location: sympy/core/power.py:1500
---

## Candidate Summary

`series((x**3)**(1/3), x, -1, 2)` returns `x`, but the principal branch near negative real `x` is complex-valued.

## Call Path

`Expr.series()` shifts the expansion point by substituting `x -> -1 + t` and then calls `_eval_nseries()` on `((t - 1)**3)**(1/3)`. That dispatches to `Pow._eval_nseries()` in `sympy/core/power.py`.

## Root Cause

At `sympy/core/power.py:1500-1503`, `Pow._eval_nseries()` unconditionally does:

```python
self = powdenest(self, force=True).trigsimp()
```

For the shifted expression, `powdenest(..., force=True)` rewrites `((t - 1)**3)**(1/3)` to `t - 1`. This denesting is not valid on the principal branch near `t = 0`, where `t - 1` is negative real.

## Mechanism

After the forced denest, the series engine expands the wrong expression `t - 1`. Substituting back gives `x`. The branch-aware leading-term code later in `Pow._eval_as_leading_term()` would return `exp(I*pi/3)` at the same point, but it never gets a chance to preserve the branch because `_eval_nseries()` has already replaced the expression by `t - 1`.

## Suggested Fix Direction

Avoid `powdenest(force=True)` in `Pow._eval_nseries()` when a noninteger exponent is applied to a power whose base can lie on or cross a principal branch cut at the expansion point. Use branch-aware leading-term logic before denesting, or only denest under assumptions that make `(a**m)**r = a**(m*r)` valid.

## Confidence and Caveats

The probe showed `shifted powdenest(force=True): y - 1`, `shifted nseries: y - 1`, and `shifted as_leading_term: exp(I*pi/3)`. That isolates the bad transformation to the forced denesting line.
