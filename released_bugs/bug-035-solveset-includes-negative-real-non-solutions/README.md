# Candidate Bug 35: solveset says every nonzero complex number satisfies sqrt(x)*sqrt(1/x) = 1

## Status

Confirmed

## SymPy version

SymPy version: 1.14.0

SYMPY_CHECKOUT_PATH: `$SYMPY_CHECKOUT_PATH`

SymPy file: `$SYMPY_CHECKOUT_PATH/sympy/__init__.py`

Python executable: `python3`

Commit hash: None

## Minimal reproducer

```python
import os
import sys

SYMPY_CHECKOUT_PATH = os.environ.get("SYMPY_CHECKOUT_PATH")
if not SYMPY_CHECKOUT_PATH:
    raise RuntimeError("SYMPY_CHECKOUT_PATH is not set in the environment")
sys.path.insert(0, SYMPY_CHECKOUT_PATH)

import sympy
from sympy import *

print("SymPy version:", sympy.__version__)
print("SymPy file:", sympy.__file__)
print("Python executable:", sys.executable)

x = symbols("x")
lhs = sqrt(x) * sqrt(1/x)
sol = solveset(Eq(lhs, 1), x, domain=S.Complexes)

print("solution:", sol)
print("contains -1:", sol.contains(S.NegativeOne))
print("lhs at -1:", lhs.subs(x, -1))
print("rhs:", S.One)
print("residual at -1:", (lhs - 1).subs(x, -1))
```

## Actual output

```text
SymPy version: 1.14.0
SymPy file: $SYMPY_CHECKOUT_PATH/sympy/__init__.py
Python executable: python3
solution: Complement(Complexes, {0})
contains -1: True
lhs at -1: -1
rhs: 1
residual at -1: -2
```

## Expected output

`-1` must not be included in the solution set. More generally, the principal-branch complex solution set should exclude zero and the negative real axis; it is not `Complement(Complexes, {0})`.

## Why this is wrong

The complex square root in SymPy is the principal square root, so square roots are not multiplicative across the negative real branch cut. At the concrete point `x = -1`,

```text
sqrt(x)*sqrt(1/x) = sqrt(-1)*sqrt(-1) = I*I = -1
```

which is not equal to `1`. Therefore any solution set that contains `-1` is mathematically false.

Equivalently, write `x = r*exp(I*theta)` with principal argument `theta` in `(-pi, pi]`. For `theta` in `(-pi, pi)`, the reciprocal has argument `-theta` and the product of principal square roots is `1`. For negative real `x`, `theta = pi` and `1/x` is also negative real, so both square roots have argument `pi/2` and the product is `-1`.

## Root cause

The diagnosis in `root_cause.md` locates the fault in `sympy/solvers/solveset.py`, function `_solve_radical`, lines 1090-1139. The public `solveset` call reaches `_solve_radical` after `unrad(sqrt(x)*sqrt(1/x) - 1, x)` returns the radical-free superset equation `(0, [])`; after denominator removal this becomes `Complement(Complexes, {0})`.

The faulty step is the `check_set` fallback at lines 1133-1135, which returns broad non-finite sets unchanged instead of validating them against the original radical equation or wrapping them in a condition. That leaves the principal-square-root branch failure on the negative real axis unchecked.

## Independent verification

`related_bugs.py` checks the representative case and five additional negative-real instantiations. For each case it verifies that SymPy's returned set contains the value, while direct SymPy substitution and an independent `cmath` principal-square-root computation both give residual `-2`.

Representative independent evidence:

```text
x=-1 sol=Complement(Complexes, {0}) contains=True sympy_lhs=-1 sympy_residual=-2 oracle_lhs=(-1+0j) oracle_residual=(-2+0j)
```

Running the script on SymPy 1.14.0 prints `Incorrect` and exits with status 1.

## Additional instantiations

The same error pattern is covered in `related_bugs.py` and mirrored in `pr/tests/test_bug_035_solveset_says_every_nonzero_complex_number_satisfies_sqrt_x.py` for:

```text
x = -2
x = -3
x = -1/2
x = -5
x = -7/3
```

## Affected function or subsystem

Solvers / `solveset` / radical equation solving. Source diagnosis: `sympy/solvers/solveset.py`, `_solve_radical`, lines 1090-1139, especially the unchecked `check_set` fallback at lines 1133-1135.

## Severity

High

SymPy returns a mathematically false solution set over `S.Complexes`, including an infinite family of non-solutions on the negative real axis.

## Suggested regression test

The proposed regression test is in:

`pr/tests/test_bug_035_solveset_says_every_nonzero_complex_number_satisfies_sqrt_x.py`

It is a single parametrized pytest file using SymPy's normal test-suite import style.

## Confidence

94%. The result is contradicted by direct substitution, by the principal-square-root branch definition, by an independent `cmath` check, and by the localized source diagnosis.
