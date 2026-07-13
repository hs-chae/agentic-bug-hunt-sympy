---
diagnosis_status: located
confidence: 90
location: sympy/solvers/inequalities.py:520 and sympy/solvers/solveset.py:230
---

## Candidate Summary

`solve_univariate_inequality(atan(x) < pi, x, relational=False)` returns `Union(Interval.open(-oo, 0), Interval.open(0, oo))`, omitting `0`.  This is wrong because `atan(0) = 0 < pi`, and in fact the inequality is true for every real `x`.

## Call Path

The public call is `solve_univariate_inequality(atan(x) < pi, x, relational=False)`.

Inside `sympy/solvers/inequalities.py:solve_univariate_inequality`, the expression is converted to `e = atan(x) - pi` at line 483.  The periodic shortcut does not apply (`periodicity(e, x)` is `None`).  The solver calls `solvify(e, x, S.Reals)` at line 520 to find critical boundary points.  `solvify` calls `solveset` (`sympy/solvers/solveset.py:2625`), and because of the same inverse-range bug as candidate 101, `solveset(atan(x) - pi, x, S.Reals)` returns `{0}`.

The scratch tracer confirmed:

```text
periodicity(atan(x) - pi, x) -> None
solvify(atan(x) - pi, x, S.Reals) -> [0]
continuous_domain(atan(x) - pi, x, S.Reals) -> Reals
```

## Root Cause

There are two linked faulty steps:

1. `sympy/solvers/solveset.py:_invert_real`, lines 230-238, accepts `x = tan(pi) = 0` for `atan(x) = pi` without checking `atan`'s principal range.
2. `sympy/solvers/inequalities.py:solve_univariate_inequality`, lines 520 and 572-658, trusts the returned `solvify` roots as critical points.  For a strict inequality, line 656 sets `_valid = include_x`, which is `False`, so the bogus boundary point `0` is removed even though direct evaluation of the inequality at `0` is true.

## Mechanism

The inequality solver partitions the real line at the roots of the equality `atan(x) - pi = 0`.  Because `solvify` incorrectly returns `[0]`, the partition is `(-oo, 0)`, `{0}`, `(0, oo)`.  The interval test `valid(_pt(start, end))` succeeds on both open intervals, so they are included.  At the critical point itself, the solver assumes it is a genuine equality root and excludes it for the strict `<` relation.  The direct `valid(0)` result is never used for ordinary roots in this branch.

## Suggested Fix Direction

Fixing the `atan` equation inversion will prevent the spurious critical point.  Independently, the inequality solver could be more robust by validating candidate critical points against the original inequality before excluding them for strict inequalities, especially when roots come from branch-sensitive transcendental solving.

## Confidence and Caveats

Confidence is high because the internal trace shows the exact bogus `solvify` root and the inequality partitioning code explains the missing singleton.  This candidate is downstream of candidate 101, but it has its own visible failure mode in how strict critical points are handled.
