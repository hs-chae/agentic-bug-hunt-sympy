# solveset finds real solutions for acos(cos(x)) = -1 even though the left side is never negative

## Summary

This adds a regression test for a confirmed correctness bug in `solveset(Eq(acos(cos(u)), -1), u, S.Reals)`. SymPy currently returns a mathematically false result or raises during a valid membership query.

## Reproducer

Run `reproduce_bug.py` from the artifact bundle with `SYMPY_CHECKOUT_PATH` pointing at the checkout. The observed SymPy 1.14.0 output is included in the bundle README.

## Expected behavior

EmptySet.

## Evidence

The bundled `related_bugs.py` checks six instantiations and includes direct substitution or an independent numerical oracle. Current SymPy prints `Incorrect` and exits nonzero.

## Suggested regression test

The test in `pr/tests/test_bug_031_solveset-finds-real-solutions-for-acos-cos-x-1-even-though-t.py` is written in SymPy test style and can be placed in the relevant solver or sets test module.
