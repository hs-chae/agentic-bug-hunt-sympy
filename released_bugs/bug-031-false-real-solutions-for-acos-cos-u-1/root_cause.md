---
diagnosis_status: located
confidence: 90
location: sympy/solvers/solveset.py:230 and sympy/solvers/solveset.py:410
---

## Candidate Summary

`solveset(Eq(acos(cos(u)), -1), u, S.Reals)` returns real `ImageSet` families such as `u = 1 + 2*pi*n`. This is impossible: for real `u`, `acos(cos(u))` lies in `[0, pi]`, so it can never equal `-1`.

## Call Path

The public call enters `solveset` and reaches `_solveset(..., _check=True)` at `sympy/solvers/solveset.py:2517`. `_solveset` rewrites the equation to `acos(cos(u)) + 1` at `sympy/solvers/solveset.py:1299-1300`, then calls `_invert` at `sympy/solvers/solveset.py:1313`.

Because the domain is real, `_invert` calls `_invert_real` (`sympy/solvers/solveset.py:178-180`). `_invert_real` strips the `+1` at `sympy/solvers/solveset.py:243-247`, reducing to `acos(cos(u)) = -1`. It then applies the generic inverse-function block at `sympy/solvers/solveset.py:230-238` to `acos`, replacing the target `-1` by `cos(-1) = cos(1)`. The remaining equation `cos(u) = cos(1)` is handled by the real trigonometric inversion block at `sympy/solvers/solveset.py:410-439`, producing the two periodic real families.

## Root Cause

The primary faulty step is `_invert_real`'s generic inverse-function branch at `sympy/solvers/solveset.py:230-238`. It applies `acos.inverse()`, i.e. `cos`, to the right-hand side without checking whether the requested value `-1` is in the principal range of `acos`.

The real trigonometric inversion block at `sympy/solvers/solveset.py:410-439` then correctly solves the transformed equation `cos(u) = cos(1)`, but by then the invalid outer inverse step has already changed the problem. Its range check at lines 425-434 checks `cos(1) in [-1, 1]`, which is true; it does not know that the original target `-1` was outside `acos`'s range.

## Mechanism

Solving `acos(cos(u)) = -1` should stop immediately because `-1` is outside the range of principal `acos`. Instead, `_invert_real` treats `acos` as algebraically invertible and maps the equation to `cos(u) = cos(-1)`. That equation has real solutions, so `_invert_trig_hyp_real` returns `u = 2*pi*n + acos(cos(1))` and `u = 2*pi*n - acos(cos(1))`, simplified to the reported families.

For a representative returned value `u = 1`, the transformed equation is true, but the original equation is false: `acos(cos(1)) = 1`, so the original residual is `2`.

As with the other solver cases, `_check=True` only calls `domain_check` for finite sets and does not validate infinite `ImageSet` families against the original residual.

## Suggested Fix Direction

Inverse trigonometric functions should not be handled by the generic inverse branch unless the right-hand side is constrained to the principal inverse function's range. For `acos`, real inversion should intersect the target set with `[0, pi]` before applying `cos`, which would make this reproducer empty.

## Confidence and Caveats

Confidence is high because direct `_invert(acos(cos(u)), -1, u, S.Reals)` returns the same `ImageSet` union as `solveset`. The secondary trig solver is not itself wrong for `cos(u) = cos(1)`; the bug is the earlier unguarded `acos` inversion.
