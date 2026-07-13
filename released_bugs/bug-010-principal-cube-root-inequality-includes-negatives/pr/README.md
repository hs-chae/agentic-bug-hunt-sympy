# Fix solve_univariate_inequality includes negative reals for a principal cube-root inequality

## Summary

This PR should fix a correctness bug in `solvers.inequalities / fractional powers / real-domain filtering`. The current SymPy 1.14.0 behavior returns a mathematically false result for `solve_univariate_inequality(x**(S(1)/3) <= m, x, relational=False)`.

## Reproducer

The local artifact includes `reproduce_bug.py`; the relevant current output is:

```text
solution: Interval(-oo, 1); contains_minus_one: True; lhs_at_minus_one: 0.5 + 0.866025403784438646763723170753*I
```

## Expected behavior

Interval(0, m**3).

## Evidence

`related_bugs.py` exercises six parametrized cases and uses a definition-based or independent numerical check. On the current version it reports `Incorrect`.

## Root cause

continuous_domain assumes odd-denominator fractional powers are real-valued on all real bases, so the inequality solver samples and accepts an interval containing negative inputs. The missing domain restriction comes from principal Pow semantics; see root_cause.md.

## Suggested regression test

Add `pr/tests/test_bug_010_solve_univariate_inequality_includes_negative_reals_for_a_pr.py` to the appropriate SymPy test directory, or move its parametrized test into an existing subsystem test file.
