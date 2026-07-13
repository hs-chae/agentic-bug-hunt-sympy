---
diagnosis_status: located
confidence: 90
location: sympy/calculus/util.py:116 and sympy/solvers/inequalities.py:508
---

## Candidate Summary

`continuous_domain(sqrt(sin(x)), x, S.Reals)` returns `Interval(0, pi)`, so it misses later real intervals such as `[2*pi, 3*pi]` where `sin(x) >= 0` and `sqrt(sin(x))` is real-valued and continuous.

## Call Path

The public call is `sympy.calculus.util.continuous_domain`. For the outer square root, `continuous_domain` iterates over `Pow` atoms and imposes `atom.base >= 0`. In this reproducer that calls `solve_univariate_inequality(sin(x) >= 0, x).as_set()`, then intersects the result with `S.Reals`.

## Root Cause

The responsible code is in `sympy/calculus/util.py:111-118`, where every non-odd rational `Pow` exponent is handled by asking `solve_univariate_inequality(atom.base >= 0, symbol)` for a set constraint.

For `sin(x) >= 0`, the faulty result is produced in `sympy/solvers/inequalities.py:483-512`. `solve_univariate_inequality` detects that the inequality expression is periodic, computes the period, and when the current domain is unbounded (`S.Reals`) it replaces the solving domain with `Interval(0, period, False, True)` at lines 508-511. It then solves only on that single period and returns the single-period set as the final answer. There is no later lifting of the interval solution back over all periods.

## Mechanism

For `sqrt(sin(x))`, `continuous_domain` needs the real radical constraint `sin(x) >= 0`. The inequality solver detects period `2*pi`, narrows `S.Reals` to `[0, 2*pi)`, and finds the true part `[0, pi]` inside that one period. Because the solver returns that set directly rather than an `ImageSet` or periodic union, `continuous_domain` intersects `S.Reals` with only `Interval(0, pi)`.

Thus `5*pi/2` is excluded even though it is just `pi/2 + 2*pi`, and `sin(5*pi/2) = 1`.

## Suggested Fix Direction

For periodic inequalities over unbounded real domains, `solve_univariate_inequality` should either return a periodic set constructed from the solved fundamental-domain pieces, or decline/return a condition set instead of returning only the fundamental-domain slice. `continuous_domain` would then receive the full periodic radical constraint.

## Confidence and Caveats

Confidence is high. The trace showed `solve_univariate_inequality(sin(x) >= 0, x)` returning exactly `(0 <= x) & (x <= pi)`, and `continuous_domain` directly uses that result for the square-root base constraint.
