---
diagnosis_status: located
confidence: 91
location: sympy/calculus/util.py:111
---

## Candidate Summary

`solve_univariate_inequality(x**(1/3) <= 1, x, relational=False)` returns `Interval(-oo, 1)`, which includes negative real values where SymPy's principal `x**(1/3)` is non-real.

## Call Path

The public call enters `sympy/solvers/inequalities.py:solve_univariate_inequality`. It forms `e = x**(1/3) - 1`, gets the equality root `x = 1` through `solvify`, and then computes the real continuity domain with `continuous_domain(expanded_e, x, S.Reals)`.

The interval-building code then tests sample points between critical points in `solve_univariate_inequality`.

## Root Cause

The primary faulty code is in `sympy/calculus/util.py:continuous_domain`, lines 111-118. For every `Pow`, it checks the exponent denominator, and if the exponent is rational with odd denominator it does nothing:

`if atom.exp.is_rational and den.is_odd: pass`

This assumes odd-denominator fractional powers are real-valued on all real bases, matching `real_root` semantics rather than principal `Pow` semantics.

The bad domain then feeds `sympy/solvers/inequalities.py:solve_univariate_inequality`, lines 563-567 and 643-667. Since the domain is incorrectly `Reals`, the solver tests one point in the interval `(-oo, 1)` and adds the whole interval when that sample satisfies the inequality.

## Mechanism

For `x**(1/3) - 1`, `continuous_domain` returns `Reals` instead of restricting the principal fractional power to the real-valued region `x >= 0`. The only equality root is `1`, so the interval solver tests the interval `(-oo, 1)` using `_pt(-oo, 1)`, which is `1/2`. At that sample the inequality is true, so it appends `Interval(-oo, 1)` wholesale. No later filter removes negative points whose left-hand side is complex.

## Suggested Fix Direction

Make `continuous_domain` distinguish principal `Pow` from real roots. For rational non-integer powers of a real expression, require the base to be nonnegative unless SymPy can prove the principal value remains real on a larger set. The inequality solver should also intersect interval results with the real-valued domain of the relational expression.

## Confidence and Caveats

Confidence is high. Runtime tracing confirmed `continuous_domain(x**(1/3) - 1, x, S.Reals)` returns `Reals`, and `solve_univariate_inequality` then constructs `Interval(-oo, 1)` by interval sampling.
