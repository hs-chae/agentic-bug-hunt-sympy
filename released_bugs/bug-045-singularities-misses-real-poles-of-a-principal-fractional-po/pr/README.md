# singularities misses real poles of 1/((x**2)**(1/3) - 1)

## Summary

This adds a regression test for a SymPy 1.14.0 correctness bug: `singularities(1/((x**2)**Rational(1, 3) - 1), x, S.Reals)` returns a mathematically false result.

## Reproducer

Run `reproduce_bug.py` from the artifact bundle with `SYMPY_CHECKOUT_PATH` set to the target checkout. The current output includes:

```text
SymPy version: 1.14.0
SymPy file: $SYMPY_CHECKOUT_PATH/sympy/__init__.py
Python executable: python3
singularities(1/((x**2)**Rational(1, 3) - 1), x, S.Reals) = EmptySet
value at x = 1: zoo
value at x = -1: zoo
```

## Expected behavior

The real singularities include {-1, 1}.

## Evidence

`related_bugs.py` checks the representative case plus five additional instantiations and fails on the current implementation. The mathematical issue is: The denominator is zero whenever x**2 = 1. At x = -1 and x = 1 the reciprocal is infinite, so both points are real singularities.

## Root cause

`singularities` asks `solveset` for denominator zeros. In the real-domain path, the equation is rewritten to an absolute-value equation, and `_invert_abs` in `sympy/solvers/solveset.py:612-617` rejects an entire finite target set if any target is negative. It discards the valid `Abs(x) = 1` branch along with the invalid one. See `root_cause.md`.

## Suggested regression test

The proposed test is in `pr/tests/test_bug_045_singularities_misses_real_poles_of_1_x_2_1_3_1.py` and uses one `pytest.mark.parametrize` block for all cases.
