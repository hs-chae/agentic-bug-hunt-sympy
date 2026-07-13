# Fix singularities misses the Chi(x) logarithmic singularity at zero

## Summary

SymPy currently returns an incorrect result for `singularities(Chi(x), x, S.Complexes)`.

## Reproducer

```python
# See ../reproduce_bug.py for the checkout-pinned full script.
singularities(Chi(x), x, S.Complexes)
```

Current output:

```text
SymPy version: 1.14.0
SymPy file: $SYMPY_CHECKOUT_PATH/sympy/__init__.py
Python executable: python3
actual_singularities = EmptySet
expected_contains_zero = False
Chi(0) = zoo
right_limit = -oo
mpmath_chi_1e_20 = -45.474486194979380819753317003604881720979845436636
```

## Expected behavior

A set containing `0`, for example `{0}`.

## Why this matters

The hyperbolic cosine integral has the local form Chi(x) = EulerGamma + log(x) + analytic terms near x = 0. The logarithm is singular at the origin; SymPy also evaluates `Chi(0)` to `zoo`.

## Root cause

The diagnosis locates the limitation in `sympy/calculus/singularities.py:97-107`. The routine only scans explicit negative powers, logs, and a few inverse hyperbolic atoms, so opaque `Chi(x)` contributes no candidates even though `Chi._atzero` and `_eval_as_leading_term` in `sympy/functions/special/error_functions.py` expose the singularity. See `root_cause.md` for details.

## Evidence

`related_bugs.py` contains the representative case plus five shifted instantiations and an independent numerical check. It exits nonzero on the current checkout and would print `Correct` after a fix.

## Suggested regression test

Add `pr/tests/test_bug_057_singularities_misses_the_logarithmic_singularity_of_chi_x_at.py` to the relevant SymPy test module.
