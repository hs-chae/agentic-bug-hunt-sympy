# solveset over the reals treats principal fractional-power identity as true for negative inputs

## Summary

This adds a regression test for a SymPy 1.14.0 correctness bug: `solveset(Eq((x**2)**Rational(1, 3), x**Rational(2, 3)), x, S.Reals)` returns a mathematically false result.

## Reproducer

Run `reproduce_bug.py` from the artifact bundle with `SYMPY_CHECKOUT_PATH` set to the target checkout. The current output includes:

```text
SymPy version: 1.14.0
SymPy file: $SYMPY_CHECKOUT_PATH/sympy/__init__.py
Python executable: python3
solveset(Eq((x**2)**Rational(1, 3), x**Rational(2, 3)), x, S.Reals) = Reals
lhs at x = -1: 1
rhs at x = -1: (-1)**(2/3)
numeric residual at x = -1: 1.5 - 0.866025403784438646763723170753*I
```

## Expected behavior

The real solution set must exclude negative real numbers; in the representative case it is Interval(0, oo).

## Evidence

`related_bugs.py` checks the representative case plus five additional instantiations and fails on the current implementation. The mathematical issue is: Principal powers use the complex principal branch. For negative real x, ((x**2)**(1/3)) is positive real, while x**(2/3) is exp(2*pi*I/3)*abs(x)**(2/3), so the two sides differ.

## Root cause

`unrad` in `sympy/solvers/solvers.py:3535-3538` cubes both radical terms and turns `(x**2)**(1/3) = x**(2/3)` into the identity `x**2 = x**2`. `_solve_radical` accepts the resulting whole-domain solve without checking the lost branch condition. See `root_cause.md` for details.

## Suggested regression test

The proposed test is in `pr/tests/test_bug_030_solveset_over_the_reals_treats_principal_fractional_power_id.py` and uses one `pytest.mark.parametrize` block for all cases.
